// frontend/components/RecommendationPanel.tsx
'use client';
import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";

interface Suggestion {
  type: string;
  instrument: string;
  title: string;
  description: string;
  prompt: string;
  color: string;
  confidence?: number;
}

interface Props {
  suggestions: Suggestion[];
  onSelect: (suggestion: Suggestion) => void;
  isLoading?: boolean;
}

// Icons as components
const ArrowIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
  </svg>
);

const SparkleIcon = () => (
  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
    <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" />
  </svg>
);

export default function RecommendationPanel({ suggestions, onSelect, isLoading = false }: Props) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  
  if ((!suggestions || suggestions.length === 0) && !isLoading) return null;

  const getTypeLabel = (type: string) => {
    const labels: Record<string, { text: string; color: string }> = {
      essential: { text: 'ESSENTIAL', color: 'text-green-400' },
      creative: { text: 'CREATIVE', color: 'text-purple-400' },
      experimental: { text: 'EXPERIMENTAL', color: 'text-yellow-400' },
      technique: { text: 'PRO TIP', color: 'text-blue-400' },
      variation: { text: 'VARIATION', color: 'text-red-400' }
    };
    return labels[type] || { text: type.toUpperCase(), color: 'text-neutral-400' };
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full mt-8"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="flex items-center gap-2">
          <SparkleIcon />
          <span className="text-sm font-bold text-neutral-400 uppercase tracking-wider">
            AI Recommendations
          </span>
        </div>
        <div className="h-[1px] bg-gradient-to-r from-neutral-800 to-transparent flex-1" />
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-32 rounded-xl bg-neutral-900/50 animate-pulse" />
          ))}
        </div>
      )}

      {/* Suggestions Grid */}
      {!isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <AnimatePresence>
            {suggestions.map((suggestion, idx) => {
              const typeInfo = getTypeLabel(suggestion.type);
              
              return (
                <motion.button
                  key={`${suggestion.type}-${idx}`}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ delay: idx * 0.1 }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => onSelect(suggestion)}
                  onMouseEnter={() => setHoveredIndex(idx)}
                  onMouseLeave={() => setHoveredIndex(null)}
                  className={`
                    relative text-left p-5 rounded-xl border transition-all duration-200
                    bg-gradient-to-b from-neutral-900/80 to-neutral-950/80 backdrop-blur
                    hover:from-neutral-800/80 hover:to-neutral-900/80
                    ${suggestion.color} border-opacity-40 hover:border-opacity-100
                    group overflow-hidden
                  `}
                >
                  {/* Background glow effect */}
                  <div 
                    className={`
                      absolute inset-0 opacity-0 group-hover:opacity-20 transition-opacity duration-300
                      bg-gradient-to-br ${suggestion.color.replace('border', 'from')} to-transparent
                    `} 
                  />
                  
                  {/* Content */}
                  <div className="relative z-10">
                    {/* Header */}
                    <div className="flex justify-between items-start mb-3">
                      <span className={`
                        text-[10px] font-bold px-2 py-1 rounded
                        bg-black/50 ${typeInfo.color} uppercase tracking-wider
                      `}>
                        {typeInfo.text}
                      </span>
                      
                      {suggestion.confidence && (
                        <div className="flex items-center gap-1">
                          {[...Array(Math.round(suggestion.confidence * 5))].map((_, i) => (
                            <div
                              key={i}
                              className="w-1 h-3 bg-gradient-to-t from-neutral-600 to-neutral-400 rounded-full"
                            />
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Title */}
                    <h4 className="text-sm font-bold text-neutral-100 mb-2 flex items-center gap-2">
                      {suggestion.title}
                      <ArrowIcon />
                    </h4>
                    
                    {/* Description */}
                    <p className="text-xs text-neutral-400 leading-relaxed mb-3">
                      {suggestion.description}
                    </p>
                    
                    {/* Instrument tag */}
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-neutral-500 uppercase">
                        Generates:
                      </span>
                      <span className="text-[10px] font-bold text-neutral-300 uppercase">
                        {suggestion.instrument}
                      </span>
                    </div>
                  </div>
                  
                  {/* Hover indicator */}
                  {hoveredIndex === idx && (
                    <motion.div
                      layoutId="hoverIndicator"
                      className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 to-purple-500"
                      initial={{ scaleX: 0 }}
                      animate={{ scaleX: 1 }}
                      transition={{ duration: 0.2 }}
                    />
                  )}
                </motion.button>
              );
            })}
          </AnimatePresence>
        </div>
      )}

      {/* Footer tip */}
      {suggestions.length > 0 && (
        <p className="text-xs text-neutral-600 text-center mt-4">
          Click any suggestion to generate instantly with AI
        </p>
      )}
    </motion.div>
  );
}