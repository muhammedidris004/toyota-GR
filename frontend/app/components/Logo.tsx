'use client'

interface LogoProps {
  size?: 'sm' | 'md' | 'lg'
  showText?: boolean
  className?: string
}

export default function Logo({ size = 'md', showText = true, className = '' }: LogoProps) {
  const sizes = {
    sm: { icon: 32, text: 'text-lg' },
    md: { icon: 40, text: 'text-xl' },
    lg: { icon: 56, text: 'text-2xl' }
  }

  const { icon, text } = sizes[size]

  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      {/* Professional Logo Icon - Racing Circuit + AI Integration */}
      <div className="relative">
        <svg
          width={icon}
          height={icon}
          viewBox="0 0 80 80"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="drop-shadow-lg"
        >
          {/* Outer Ring - Track Circuit */}
          <circle
            cx="40"
            cy="40"
            r="36"
            stroke="url(#redGradient)"
            strokeWidth="2.5"
            fill="none"
            opacity="0.9"
          />
          
          {/* Inner Circuit Pattern - Racing Track */}
          <path
            d="M 20 40 Q 25 20, 40 20 Q 55 20, 60 40 Q 55 60, 40 60 Q 25 60, 20 40"
            stroke="url(#neonGradient)"
            strokeWidth="2.5"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          
          {/* AI Neural Network Nodes */}
          <circle cx="30" cy="30" r="4" fill="#00FF88" opacity="0.9">
            <animate attributeName="opacity" values="0.5;1;0.5" dur="2s" repeatCount="indefinite" />
          </circle>
          <circle cx="50" cy="30" r="4" fill="#00FF88" opacity="0.9">
            <animate attributeName="opacity" values="0.5;1;0.5" dur="2s" begin="0.3s" repeatCount="indefinite" />
          </circle>
          <circle cx="40" cy="40" r="5" fill="#E60012">
            <animate attributeName="r" values="4;5.5;4" dur="2s" repeatCount="indefinite" />
          </circle>
          <circle cx="30" cy="50" r="4" fill="#00FF88" opacity="0.9">
            <animate attributeName="opacity" values="0.5;1;0.5" dur="2s" begin="0.6s" repeatCount="indefinite" />
          </circle>
          <circle cx="50" cy="50" r="4" fill="#00FF88" opacity="0.9">
            <animate attributeName="opacity" values="0.5;1;0.5" dur="2s" begin="0.9s" repeatCount="indefinite" />
          </circle>
          
          {/* Connection Lines - AI Network */}
          <line x1="30" y1="30" x2="40" y2="40" stroke="#00FF88" strokeWidth="1.5" opacity="0.4" />
          <line x1="50" y1="30" x2="40" y2="40" stroke="#00FF88" strokeWidth="1.5" opacity="0.4" />
          <line x1="30" y1="50" x2="40" y2="40" stroke="#00FF88" strokeWidth="1.5" opacity="0.4" />
          <line x1="50" y1="50" x2="40" y2="40" stroke="#00FF88" strokeWidth="1.5" opacity="0.4" />
          
          {/* Tire Tread Pattern - Subtle */}
          <path
            d="M 25 35 L 30 35 M 50 35 L 55 35 M 25 45 L 30 45 M 50 45 L 55 45"
            stroke="#2C2C2C"
            strokeWidth="2"
            strokeLinecap="round"
            opacity="0.6"
          />
          
          {/* Speed Lines */}
          <path
            d="M 15 40 L 20 40 M 60 40 L 65 40"
            stroke="#E60012"
            strokeWidth="2"
            strokeLinecap="round"
            opacity="0.7"
          />
          
          {/* Gradients */}
          <defs>
            <linearGradient id="redGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#E60012" />
              <stop offset="100%" stopColor="#FF3366" />
            </linearGradient>
            <linearGradient id="neonGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#00FF88" />
              <stop offset="100%" stopColor="#00CC6A" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      {/* Logo Text */}
      {showText && (
        <div className="flex flex-col">
          <span className={`font-bold ${text} bg-gradient-to-r from-[#E60012] via-[#FF3366] to-[#E60012] bg-clip-text text-transparent tracking-tight`}>
            GR
          </span>
          <span className="text-xs text-gr-grey font-medium -mt-1 tracking-wider uppercase">
            Race Strategist AI
          </span>
        </div>
      )}
    </div>
  )
}
