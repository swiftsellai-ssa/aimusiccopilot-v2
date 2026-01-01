# backend/routers/analytics.py
"""
Analytics tracking and reporting endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from typing import Optional
from datetime import timedelta
import datetime as dt
from pydantic import BaseModel
from jose import jwt

from database import get_db
from models.models import User
from models.analytics import GenerationEvent, UserSession, AnalyticsSummary
from utils.security import ALGORITHM, SECRET_KEY


router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


# Auth helper - Get current user from JWT token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user from JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    # Get user from database
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme_optional), db: Session = Depends(get_db)) -> Optional[User]:
    """Get current user if authenticated, None otherwise (for public endpoints)"""
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return db.query(User).filter(User.email == email).first()
    except Exception:
        return None


# ============= Pydantic Models =============

class TrackGenerationRequest(BaseModel):
    """Track a MIDI generation event"""
    mode: str  # 'simple' or 'advanced'
    generation_type: str  # 'drums', 'bass', 'melody', 'full'
    style: str
    bpm: int
    musical_key: Optional[str] = None
    musical_scale: Optional[str] = None

    # DNA parameters (optional)
    density: Optional[float] = None
    complexity: Optional[float] = None
    groove: Optional[float] = None
    evolution: Optional[float] = None
    bars: Optional[int] = None

    # Outcome
    success: bool = True
    error_message: Optional[str] = None
    generation_time_ms: Optional[int] = None


class TrackInteractionRequest(BaseModel):
    """Track user interaction with generated MIDI"""
    event_id: int
    action: str  # 'download', 'play', 'stop'
    play_duration_seconds: Optional[float] = None


class AnalyticsResponse(BaseModel):
    """Analytics dashboard data"""
    # Overall stats
    total_generations: int
    successful_generations: int
    failed_generations: int
    success_rate: float

    # Mode breakdown
    simple_mode_percentage: float
    advanced_mode_percentage: float

    # Most popular settings
    most_popular_type: str
    most_popular_style: str
    most_popular_key: Optional[str]
    most_popular_scale: Optional[str]

    # Averages
    avg_bpm: float
    avg_generation_time_ms: float

    # DNA averages (advanced mode only)
    avg_density: Optional[float]
    avg_complexity: Optional[float]
    avg_groove: Optional[float]
    avg_evolution: Optional[float]
    avg_bars: Optional[float]

    # Engagement
    download_rate: float
    play_rate: float
    avg_play_duration: Optional[float]

    # Time period
    period_days: int


# ============= Tracking Endpoints =============

@router.post("/track/generation")
async def track_generation(
    data: TrackGenerationRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Track a MIDI generation event"""

    # Create generation event
    event = GenerationEvent(
        user_id=current_user.id,
        mode=data.mode,
        generation_type=data.generation_type,
        style=data.style,
        bpm=data.bpm,
        musical_key=data.musical_key,
        musical_scale=data.musical_scale,
        density=data.density,
        complexity=data.complexity,
        groove=data.groove,
        evolution=data.evolution,
        bars=data.bars,
        success=data.success,
        error_message=data.error_message,
        generation_time_ms=data.generation_time_ms,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return {
        "event_id": event.id,
        "message": "Generation tracked successfully"
    }


@router.post("/track/interaction")
async def track_interaction(
    data: TrackInteractionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Track user interaction with generated MIDI (play, download)"""

    # Find the event
    event = db.query(GenerationEvent).filter(
        GenerationEvent.id == data.event_id,
        GenerationEvent.user_id == current_user.id
    ).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Update event based on action
    if data.action == "download":
        event.was_downloaded = True
    elif data.action == "play":
        event.was_played = True
        if data.play_duration_seconds:
            event.play_duration_seconds = data.play_duration_seconds

    db.commit()

    return {"message": f"{data.action.capitalize()} tracked successfully"}


@router.post("/track/session/start")
async def start_session(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Start tracking a user session"""

    user_id = current_user.id if current_user else None

    session = UserSession(
        user_id=user_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "message": "Session started"
    }


@router.post("/track/session/end/{session_id}")
async def end_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """End a user session"""

    user_id = current_user.id if current_user else None

    session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.user_id == user_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.session_end = dt.datetime.utcnow()
    session.duration_seconds = int((session.session_end - session.session_start).total_seconds())

    db.commit()

    return {"message": "Session ended"}


# ============= Analytics Reporting Endpoints =============

@router.get("/summary", response_model=AnalyticsResponse)
async def get_analytics_summary(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get analytics summary for the current user
    Optionally filter by time period (default: last 30 days)
    """

    # Calculate date range
    end_date = dt.datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Query events within date range
    events = db.query(GenerationEvent).filter(
        GenerationEvent.user_id == current_user.id,
        GenerationEvent.created_at >= start_date,
        GenerationEvent.created_at <= end_date
    ).all()

    if not events:
        # Return default values if no data
        return AnalyticsResponse(
            total_generations=0,
            successful_generations=0,
            failed_generations=0,
            success_rate=0.0,
            simple_mode_percentage=0.0,
            advanced_mode_percentage=0.0,
            most_popular_type="drums",
            most_popular_style="techno",
            most_popular_key=None,
            most_popular_scale=None,
            avg_bpm=128.0,
            avg_generation_time_ms=0.0,
            avg_density=None,
            avg_complexity=None,
            avg_groove=None,
            avg_evolution=None,
            avg_bars=None,
            download_rate=0.0,
            play_rate=0.0,
            avg_play_duration=None,
            period_days=days
        )

    # Calculate statistics
    total = len(events)
    successful = sum(1 for e in events if e.success)
    failed = total - successful
    success_rate = (successful / total * 100) if total > 0 else 0

    # Mode breakdown
    simple_count = sum(1 for e in events if e.mode == 'simple')
    advanced_count = sum(1 for e in events if e.mode == 'advanced')
    simple_pct = (simple_count / total * 100) if total > 0 else 0
    advanced_pct = (advanced_count / total * 100) if total > 0 else 0

    # Most popular type
    type_counts = {}
    for e in events:
        type_counts[e.generation_type] = type_counts.get(e.generation_type, 0) + 1
    most_popular_type = max(type_counts, key=type_counts.get) if type_counts else "drums"

    # Most popular style
    style_counts = {}
    for e in events:
        style_counts[e.style] = style_counts.get(e.style, 0) + 1
    most_popular_style = max(style_counts, key=style_counts.get) if style_counts else "techno"

    # Most popular key/scale
    key_counts = {}
    scale_counts = {}
    for e in events:
        if e.musical_key:
            key_counts[e.musical_key] = key_counts.get(e.musical_key, 0) + 1
        if e.musical_scale:
            scale_counts[e.musical_scale] = scale_counts.get(e.musical_scale, 0) + 1

    most_popular_key = max(key_counts, key=key_counts.get) if key_counts else None
    most_popular_scale = max(scale_counts, key=scale_counts.get) if scale_counts else None

    # Averages
    avg_bpm = sum(e.bpm for e in events) / total
    generation_times = [e.generation_time_ms for e in events if e.generation_time_ms]
    avg_gen_time = sum(generation_times) / len(generation_times) if generation_times else 0

    # DNA averages (advanced mode only)
    advanced_events = [e for e in events if e.mode == 'advanced']
    if advanced_events:
        densities = [e.density for e in advanced_events if e.density is not None]
        complexities = [e.complexity for e in advanced_events if e.complexity is not None]
        grooves = [e.groove for e in advanced_events if e.groove is not None]
        evolutions = [e.evolution for e in advanced_events if e.evolution is not None]
        bars = [e.bars for e in advanced_events if e.bars is not None]

        avg_density = sum(densities) / len(densities) if densities else None
        avg_complexity = sum(complexities) / len(complexities) if complexities else None
        avg_groove = sum(grooves) / len(grooves) if grooves else None
        avg_evolution = sum(evolutions) / len(evolutions) if evolutions else None
        avg_bars = sum(bars) / len(bars) if bars else None
    else:
        avg_density = avg_complexity = avg_groove = avg_evolution = avg_bars = None

    # Engagement metrics
    downloads = sum(1 for e in events if e.was_downloaded)
    plays = sum(1 for e in events if e.was_played)
    download_rate = (downloads / total * 100) if total > 0 else 0
    play_rate = (plays / total * 100) if total > 0 else 0

    play_durations = [e.play_duration_seconds for e in events if e.play_duration_seconds]
    avg_play_duration = sum(play_durations) / len(play_durations) if play_durations else None

    return AnalyticsResponse(
        total_generations=total,
        successful_generations=successful,
        failed_generations=failed,
        success_rate=success_rate,
        simple_mode_percentage=simple_pct,
        advanced_mode_percentage=advanced_pct,
        most_popular_type=most_popular_type,
        most_popular_style=most_popular_style,
        most_popular_key=most_popular_key,
        most_popular_scale=most_popular_scale,
        avg_bpm=avg_bpm,
        avg_generation_time_ms=avg_gen_time,
        avg_density=avg_density,
        avg_complexity=avg_complexity,
        avg_groove=avg_groove,
        avg_evolution=avg_evolution,
        avg_bars=avg_bars,
        download_rate=download_rate,
        play_rate=play_rate,
        avg_play_duration=avg_play_duration,
        period_days=days
    )


@router.get("/insights")
async def get_insights(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get personalized insights and recommendations based on usage patterns"""

    # Calculate date range
    end_date = dt.datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    events = db.query(GenerationEvent).filter(
        GenerationEvent.user_id == current_user.id,
        GenerationEvent.created_at >= start_date
    ).all()

    if not events:
        return {
            "insights": ["Start generating MIDI patterns to see personalized insights!"],
            "recommendations": []
        }

    insights = []
    recommendations = []

    # Insight: Most active mode
    simple_count = sum(1 for e in events if e.mode == 'simple')
    advanced_count = sum(1 for e in events if e.mode == 'advanced')

    if simple_count > advanced_count * 2:
        insights.append(f"You prefer Simple Mode ({simple_count} generations vs {advanced_count} in DNA Mode)")
        recommendations.append("Try DNA Mode for more control over your patterns!")
    elif advanced_count > simple_count * 2:
        insights.append(f"You're a power user! {advanced_count} DNA Mode generations vs {simple_count} Simple Mode")
        recommendations.append("Experiment with extreme DNA parameter values for unique sounds")

    # Insight: Favorite style
    style_counts = {}
    for e in events:
        style_counts[e.style] = style_counts.get(e.style, 0) + 1

    if style_counts:
        fav_style = max(style_counts, key=style_counts.get)
        count = style_counts[fav_style]
        insights.append(f"Your favorite style is {fav_style.title()} ({count} generations)")

        # Recommend other styles
        all_styles = ['techno', 'house', 'trap', 'dnb', 'lofi']
        unexplored = [s for s in all_styles if s not in style_counts]
        if unexplored:
            recommendations.append(f"Try exploring: {', '.join(s.title() for s in unexplored[:2])}")

    # Insight: BPM preferences
    avg_bpm = sum(e.bpm for e in events) / len(events)
    insights.append(f"Your average BPM is {int(avg_bpm)}")

    if avg_bpm < 100:
        recommendations.append("Try faster tempos (120-140 BPM) for energetic patterns")
    elif avg_bpm > 150:
        recommendations.append("Experiment with slower tempos (90-120 BPM) for groovy vibes")

    # Insight: Download rate
    downloads = sum(1 for e in events if e.was_downloaded)
    download_rate = (downloads / len(events) * 100)

    if download_rate > 80:
        insights.append(f"High download rate: {int(download_rate)}% - you love almost everything you generate!")
    elif download_rate < 30:
        insights.append(f"Low download rate: {int(download_rate)}% - try adjusting parameters for better results")
        recommendations.append("Iterate on patterns by tweaking DNA parameters until you find the perfect sound")

    # Insight: DNA parameter patterns
    advanced_events = [e for e in events if e.mode == 'advanced']
    if advanced_events:
        avg_density = sum(e.density for e in advanced_events if e.density) / len(advanced_events)
        if avg_density > 0.7:
            insights.append("You prefer dense, busy patterns")
            recommendations.append("Try lower density (0.3-0.5) for minimalist vibes")
        elif avg_density < 0.4:
            insights.append("You prefer sparse, minimal patterns")
            recommendations.append("Try higher density (0.7-0.9) for complex rhythms")

    return {
        "insights": insights,
        "recommendations": recommendations,
        "period_days": days
    }
