'use client'

interface ConsoleStepperProps {
  step1Complete: boolean  // Track & Race selected
  step2Complete: boolean  // Data loaded
  step3Complete: boolean  // Driver selected
  step4Complete: boolean  // Strategy ready
}

export default function ConsoleStepper({ 
  step1Complete, 
  step2Complete, 
  step3Complete, 
  step4Complete 
}: ConsoleStepperProps) {
  const steps = [
    { id: 1, label: 'Track & Race Selected', complete: step1Complete },
    { id: 2, label: 'Data Loaded', complete: step2Complete },
    { id: 3, label: 'Driver Selected', complete: step3Complete },
    { id: 4, label: 'Strategy Ready', complete: step4Complete },
  ]

  return (
    <div className="card p-6 mb-8">
      <h2 className="text-xl font-bold text-white mb-6">Setup Progress</h2>
      <div className="flex items-center justify-between">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center flex-1">
            {/* Step Circle */}
            <div className="flex flex-col items-center flex-1">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-sm transition-all ${
                step.complete
                  ? 'bg-gr-neon text-gr-black shadow-gr-neon'
                  : 'bg-gr-grey/30 text-gr-grey border-2 border-gr-grey'
              }`}>
                {step.complete ? (
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                ) : (
                  step.id
                )}
              </div>
              <p className={`text-xs mt-2 text-center max-w-[100px] ${
                step.complete ? 'text-gr-neon' : 'text-gr-grey'
              }`}>
                {step.label}
              </p>
            </div>
            
            {/* Connector Line */}
            {index < steps.length - 1 && (
              <div className={`flex-1 h-0.5 mx-2 ${
                step.complete ? 'bg-gr-neon' : 'bg-gr-grey/30'
              }`} />
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

