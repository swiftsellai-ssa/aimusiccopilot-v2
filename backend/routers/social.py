# backend/routers/social.py
"""
API endpoints for social/sharing features:
- Share generations (create shareable links)
- Public gallery (browse shared patterns)
- Upvote/downvote generations
- Preset marketplace (share & browse presets)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import secrets
import datetime as dt

from database import get_db
from models.models import User
from models.social import SharedGeneration, GenerationVote, SharedPreset, PresetVote
from pydantic import BaseModel

# JWT dependencies
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from utils.security import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user from JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[User]:
    """Get current user if authenticated, None otherwise (for public endpoints)"""
    if not token:
        return None
    try:
        return get_current_user(token, db)
    except:
        return None


router = APIRouter(prefix="/social", tags=["social"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ShareGenerationRequest(BaseModel):
    title: str
    description: Optional[str] = None
    mode: str
    type: str
    style: str
    bpm: int
    key: str
    scale: str
    density: Optional[float] = None
    complexity: Optional[float] = None
    groove: Optional[float] = None
    evolution: Optional[float] = None
    bars: Optional[int] = None
    midi_url: str


class SharePresetRequest(BaseModel):
    name: str
    description: Optional[str] = None
    mode: str
    type: str
    style: str
    bpm: int
    key: str
    scale: str
    density: float
    complexity: float
    groove: float
    evolution: float
    bars: int
    tags: Optional[str] = None
    genre: Optional[str] = None


class VoteRequest(BaseModel):
    vote_type: str  # 'upvote' or 'downvote'


class SharedGenerationResponse(BaseModel):
    id: int
    share_id: str
    user_email: str
    title: str
    description: Optional[str]
    mode: str
    type: str
    style: str
    bpm: int
    key: str
    scale: str
    density: Optional[float]
    complexity: Optional[float]
    groove: Optional[float]
    evolution: Optional[float]
    bars: Optional[int]
    midi_url: str
    view_count: int
    play_count: int
    download_count: int
    upvotes: int
    downvotes: int
    score: int
    created_at: dt.datetime
    user_vote: Optional[str] = None  # Current user's vote if any

    class Config:
        from_attributes = True


class SharedPresetResponse(BaseModel):
    id: int
    share_id: str
    user_email: str
    name: str
    description: Optional[str]
    mode: str
    type: str
    style: str
    bpm: int
    key: str
    scale: str
    density: float
    complexity: float
    groove: float
    evolution: float
    bars: int
    tags: Optional[str]
    genre: Optional[str]
    view_count: int
    use_count: int
    upvotes: int
    downvotes: int
    score: int
    created_at: dt.datetime
    user_vote: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# SHARED GENERATIONS ENDPOINTS
# ============================================================================

@router.post("/generations/share", response_model=SharedGenerationResponse)
def share_generation(
    request: ShareGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Share a generation publicly
    Creates a unique shareable link
    """
    # Generate unique share ID
    share_id = secrets.token_urlsafe(12)
    while db.query(SharedGeneration).filter(SharedGeneration.share_id == share_id).first():
        share_id = secrets.token_urlsafe(12)

    # Create shared generation
    shared_gen = SharedGeneration(
        share_id=share_id,
        user_id=current_user.id,
        title=request.title,
        description=request.description,
        mode=request.mode,
        type=request.type,
        style=request.style,
        bpm=request.bpm,
        key=request.key,
        scale=request.scale,
        density=request.density,
        complexity=request.complexity,
        groove=request.groove,
        evolution=request.evolution,
        bars=request.bars,
        midi_url=request.midi_url
    )

    db.add(shared_gen)
    db.commit()
    db.refresh(shared_gen)

    return SharedGenerationResponse(
        id=shared_gen.id,
        share_id=shared_gen.share_id,
        user_email=current_user.email,
        title=shared_gen.title,
        description=shared_gen.description,
        mode=shared_gen.mode,
        type=shared_gen.type,
        style=shared_gen.style,
        bpm=shared_gen.bpm,
        key=shared_gen.key,
        scale=shared_gen.scale,
        density=shared_gen.density,
        complexity=shared_gen.complexity,
        groove=shared_gen.groove,
        evolution=shared_gen.evolution,
        bars=shared_gen.bars,
        midi_url=shared_gen.midi_url,
        view_count=shared_gen.view_count,
        play_count=shared_gen.play_count,
        download_count=shared_gen.download_count,
        upvotes=shared_gen.upvotes,
        downvotes=shared_gen.downvotes,
        score=shared_gen.score,
        created_at=shared_gen.created_at
    )


@router.get("/generations/{share_id}", response_model=SharedGenerationResponse)
def get_shared_generation(
    share_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get a shared generation by its share ID
    Public endpoint (no auth required)
    Increments view count
    """
    shared_gen = db.query(SharedGeneration).filter(SharedGeneration.share_id == share_id).first()
    if not shared_gen:
        raise HTTPException(status_code=404, detail="Shared generation not found")

    # Increment view count
    shared_gen.view_count += 1
    db.commit()

    # Check if current user has voted
    user_vote = None
    if current_user:
        vote = db.query(GenerationVote).filter(
            GenerationVote.user_id == current_user.id,
            GenerationVote.generation_id == shared_gen.id
        ).first()
        if vote:
            user_vote = vote.vote_type

    return SharedGenerationResponse(
        id=shared_gen.id,
        share_id=shared_gen.share_id,
        user_email=shared_gen.user.email,
        title=shared_gen.title,
        description=shared_gen.description,
        mode=shared_gen.mode,
        type=shared_gen.type,
        style=shared_gen.style,
        bpm=shared_gen.bpm,
        key=shared_gen.key,
        scale=shared_gen.scale,
        density=shared_gen.density,
        complexity=shared_gen.complexity,
        groove=shared_gen.groove,
        evolution=shared_gen.evolution,
        bars=shared_gen.bars,
        midi_url=shared_gen.midi_url,
        view_count=shared_gen.view_count,
        play_count=shared_gen.play_count,
        download_count=shared_gen.download_count,
        upvotes=shared_gen.upvotes,
        downvotes=shared_gen.downvotes,
        score=shared_gen.score,
        created_at=shared_gen.created_at,
        user_vote=user_vote
    )


@router.get("/generations", response_model=List[SharedGenerationResponse])
def get_public_gallery(
    sort_by: str = Query("recent", regex="^(recent|popular|trending)$"),
    type: Optional[str] = None,
    style: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get public gallery of shared generations
    Public endpoint with optional filtering and sorting
    """
    query = db.query(SharedGeneration)

    # Apply filters
    if type:
        query = query.filter(SharedGeneration.type == type)
    if style:
        query = query.filter(SharedGeneration.style == style)

    # Apply sorting
    if sort_by == "popular":
        # Sort by score (upvotes - downvotes)
        query = query.order_by((SharedGeneration.upvotes - SharedGeneration.downvotes).desc())
    elif sort_by == "trending":
        # Sort by engagement score
        query = query.order_by(
            (SharedGeneration.view_count +
             SharedGeneration.play_count * 2 +
             SharedGeneration.download_count * 3 +
             SharedGeneration.upvotes * 5).desc()
        )
    else:  # recent
        query = query.order_by(SharedGeneration.created_at.desc())

    # Paginate
    shared_gens = query.offset(offset).limit(limit).all()

    # Build responses with user votes
    results = []
    for shared_gen in shared_gens:
        user_vote = None
        if current_user:
            vote = db.query(GenerationVote).filter(
                GenerationVote.user_id == current_user.id,
                GenerationVote.generation_id == shared_gen.id
            ).first()
            if vote:
                user_vote = vote.vote_type

        results.append(SharedGenerationResponse(
            id=shared_gen.id,
            share_id=shared_gen.share_id,
            user_email=shared_gen.user.email,
            title=shared_gen.title,
            description=shared_gen.description,
            mode=shared_gen.mode,
            type=shared_gen.type,
            style=shared_gen.style,
            bpm=shared_gen.bpm,
            key=shared_gen.key,
            scale=shared_gen.scale,
            density=shared_gen.density,
            complexity=shared_gen.complexity,
            groove=shared_gen.groove,
            evolution=shared_gen.evolution,
            bars=shared_gen.bars,
            midi_url=shared_gen.midi_url,
            view_count=shared_gen.view_count,
            play_count=shared_gen.play_count,
            download_count=shared_gen.download_count,
            upvotes=shared_gen.upvotes,
            downvotes=shared_gen.downvotes,
            score=shared_gen.score,
            created_at=shared_gen.created_at,
            user_vote=user_vote
        ))

    return results


@router.post("/generations/{share_id}/vote")
def vote_on_generation(
    share_id: str,
    request: VoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upvote or downvote a shared generation
    One vote per user per generation (can change vote)
    """
    if request.vote_type not in ["upvote", "downvote"]:
        raise HTTPException(status_code=400, detail="Invalid vote type")

    shared_gen = db.query(SharedGeneration).filter(SharedGeneration.share_id == share_id).first()
    if not shared_gen:
        raise HTTPException(status_code=404, detail="Shared generation not found")

    # Check for existing vote
    existing_vote = db.query(GenerationVote).filter(
        GenerationVote.user_id == current_user.id,
        GenerationVote.generation_id == shared_gen.id
    ).first()

    if existing_vote:
        # Update existing vote counts
        if existing_vote.vote_type == "upvote":
            shared_gen.upvotes -= 1
        else:
            shared_gen.downvotes -= 1

        # Change vote
        existing_vote.vote_type = request.vote_type
        existing_vote.updated_at = dt.datetime.utcnow()
    else:
        # Create new vote
        new_vote = GenerationVote(
            user_id=current_user.id,
            generation_id=shared_gen.id,
            vote_type=request.vote_type
        )
        db.add(new_vote)

    # Update vote counts
    if request.vote_type == "upvote":
        shared_gen.upvotes += 1
    else:
        shared_gen.downvotes += 1

    db.commit()

    return {
        "success": True,
        "upvotes": shared_gen.upvotes,
        "downvotes": shared_gen.downvotes,
        "score": shared_gen.score
    }


@router.post("/generations/{share_id}/play")
def increment_play_count(
    share_id: str,
    db: Session = Depends(get_db)
):
    """Increment play count when user plays the MIDI"""
    shared_gen = db.query(SharedGeneration).filter(SharedGeneration.share_id == share_id).first()
    if not shared_gen:
        raise HTTPException(status_code=404, detail="Shared generation not found")

    shared_gen.play_count += 1
    db.commit()

    return {"success": True, "play_count": shared_gen.play_count}


@router.post("/generations/{share_id}/download")
def increment_download_count(
    share_id: str,
    db: Session = Depends(get_db)
):
    """Increment download count when user downloads the MIDI"""
    shared_gen = db.query(SharedGeneration).filter(SharedGeneration.share_id == share_id).first()
    if not shared_gen:
        raise HTTPException(status_code=404, detail="Shared generation not found")

    shared_gen.download_count += 1
    db.commit()

    return {"success": True, "download_count": shared_gen.download_count}


# ============================================================================
# PRESET MARKETPLACE ENDPOINTS
# ============================================================================

@router.post("/presets/share", response_model=SharedPresetResponse)
def share_preset(
    request: SharePresetRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Share a custom preset to the marketplace
    Creates a unique shareable link
    """
    # Generate unique share ID
    share_id = secrets.token_urlsafe(12)
    while db.query(SharedPreset).filter(SharedPreset.share_id == share_id).first():
        share_id = secrets.token_urlsafe(12)

    # Create shared preset
    shared_preset = SharedPreset(
        share_id=share_id,
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        mode=request.mode,
        type=request.type,
        style=request.style,
        bpm=request.bpm,
        key=request.key,
        scale=request.scale,
        density=request.density,
        complexity=request.complexity,
        groove=request.groove,
        evolution=request.evolution,
        bars=request.bars,
        tags=request.tags,
        genre=request.genre or request.style
    )

    db.add(shared_preset)
    db.commit()
    db.refresh(shared_preset)

    return SharedPresetResponse(
        id=shared_preset.id,
        share_id=shared_preset.share_id,
        user_email=current_user.email,
        name=shared_preset.name,
        description=shared_preset.description,
        mode=shared_preset.mode,
        type=shared_preset.type,
        style=shared_preset.style,
        bpm=shared_preset.bpm,
        key=shared_preset.key,
        scale=shared_preset.scale,
        density=shared_preset.density,
        complexity=shared_preset.complexity,
        groove=shared_preset.groove,
        evolution=shared_preset.evolution,
        bars=shared_preset.bars,
        tags=shared_preset.tags,
        genre=shared_preset.genre,
        view_count=shared_preset.view_count,
        use_count=shared_preset.use_count,
        upvotes=shared_preset.upvotes,
        downvotes=shared_preset.downvotes,
        score=shared_preset.score,
        created_at=shared_preset.created_at
    )


@router.get("/presets", response_model=List[SharedPresetResponse])
def get_preset_marketplace(
    sort_by: str = Query("trending", regex="^(recent|popular|trending|most_used)$"),
    genre: Optional[str] = None,
    type: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Browse preset marketplace
    Public endpoint with filtering and sorting
    """
    query = db.query(SharedPreset).filter(SharedPreset.is_public == True)

    # Apply filters
    if genre:
        query = query.filter(SharedPreset.genre == genre)
    if type:
        query = query.filter(SharedPreset.type == type)

    # Apply sorting
    if sort_by == "popular":
        query = query.order_by((SharedPreset.upvotes - SharedPreset.downvotes).desc())
    elif sort_by == "most_used":
        query = query.order_by(SharedPreset.use_count.desc())
    elif sort_by == "trending":
        # Calculate trending score: (use_count + upvotes * 5) / days_old
        # Note: This is approximated in SQL - for production, consider caching
        query = query.order_by(SharedPreset.use_count.desc())
    else:  # recent
        query = query.order_by(SharedPreset.created_at.desc())

    # Paginate
    presets = query.offset(offset).limit(limit).all()

    # Build responses with user votes
    results = []
    for preset in presets:
        user_vote = None
        if current_user:
            vote = db.query(PresetVote).filter(
                PresetVote.user_id == current_user.id,
                PresetVote.preset_id == preset.id
            ).first()
            if vote:
                user_vote = vote.vote_type

        results.append(SharedPresetResponse(
            id=preset.id,
            share_id=preset.share_id,
            user_email=preset.user.email,
            name=preset.name,
            description=preset.description,
            mode=preset.mode,
            type=preset.type,
            style=preset.style,
            bpm=preset.bpm,
            key=preset.key,
            scale=preset.scale,
            density=preset.density,
            complexity=preset.complexity,
            groove=preset.groove,
            evolution=preset.evolution,
            bars=preset.bars,
            tags=preset.tags,
            genre=preset.genre,
            view_count=preset.view_count,
            use_count=preset.use_count,
            upvotes=preset.upvotes,
            downvotes=preset.downvotes,
            score=preset.score,
            created_at=preset.created_at,
            user_vote=user_vote
        ))

    return results


@router.get("/presets/{share_id}", response_model=SharedPresetResponse)
def get_shared_preset(
    share_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get a shared preset by its share ID
    Public endpoint
    Increments view count
    """
    preset = db.query(SharedPreset).filter(SharedPreset.share_id == share_id).first()
    if not preset or not preset.is_public:
        raise HTTPException(status_code=404, detail="Shared preset not found")

    # Increment view count
    preset.view_count += 1
    db.commit()

    # Check if current user has voted
    user_vote = None
    if current_user:
        vote = db.query(PresetVote).filter(
            PresetVote.user_id == current_user.id,
            PresetVote.preset_id == preset.id
        ).first()
        if vote:
            user_vote = vote.vote_type

    return SharedPresetResponse(
        id=preset.id,
        share_id=preset.share_id,
        user_email=preset.user.email,
        name=preset.name,
        description=preset.description,
        mode=preset.mode,
        type=preset.type,
        style=preset.style,
        bpm=preset.bpm,
        key=preset.key,
        scale=preset.scale,
        density=preset.density,
        complexity=preset.complexity,
        groove=preset.groove,
        evolution=preset.evolution,
        bars=preset.bars,
        tags=preset.tags,
        genre=preset.genre,
        view_count=preset.view_count,
        use_count=preset.use_count,
        upvotes=preset.upvotes,
        downvotes=preset.downvotes,
        score=preset.score,
        created_at=preset.created_at,
        user_vote=user_vote
    )


@router.post("/presets/{share_id}/use")
def increment_preset_use_count(
    share_id: str,
    db: Session = Depends(get_db)
):
    """Increment use count when user loads the preset"""
    preset = db.query(SharedPreset).filter(SharedPreset.share_id == share_id).first()
    if not preset:
        raise HTTPException(status_code=404, detail="Shared preset not found")

    preset.use_count += 1
    db.commit()

    return {"success": True, "use_count": preset.use_count}


@router.post("/presets/{share_id}/vote")
def vote_on_preset(
    share_id: str,
    request: VoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upvote or downvote a shared preset
    One vote per user per preset (can change vote)
    """
    if request.vote_type not in ["upvote", "downvote"]:
        raise HTTPException(status_code=400, detail="Invalid vote type")

    preset = db.query(SharedPreset).filter(SharedPreset.share_id == share_id).first()
    if not preset:
        raise HTTPException(status_code=404, detail="Shared preset not found")

    # Check for existing vote
    existing_vote = db.query(PresetVote).filter(
        PresetVote.user_id == current_user.id,
        PresetVote.preset_id == preset.id
    ).first()

    if existing_vote:
        # Update existing vote counts
        if existing_vote.vote_type == "upvote":
            preset.upvotes -= 1
        else:
            preset.downvotes -= 1

        # Change vote
        existing_vote.vote_type = request.vote_type
        existing_vote.updated_at = dt.datetime.utcnow()
    else:
        # Create new vote
        new_vote = PresetVote(
            user_id=current_user.id,
            preset_id=preset.id,
            vote_type=request.vote_type
        )
        db.add(new_vote)

    # Update vote counts
    if request.vote_type == "upvote":
        preset.upvotes += 1
    else:
        preset.downvotes += 1

    db.commit()

    return {
        "success": True,
        "upvotes": preset.upvotes,
        "downvotes": preset.downvotes,
        "score": preset.score
    }
