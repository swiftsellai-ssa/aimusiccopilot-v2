import React from 'react';

export default function LegalPage() {
    return (
        <div className="min-h-screen bg-gray-900 text-gray-100 p-8">
            <div className="max-w-4xl mx-auto space-y-12">
                <header className="text-center space-y-4">
                    <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
                        Legal Information
                    </h1>
                    <p className="text-gray-400">Terms of Service & Privacy Policy</p>
                </header>

                {/* Terms of Service */}
                <section>
                    <h2 className="text-2xl font-semibold mb-4 text-white">1. Terms of Service</h2>
                    <p className="mb-4 text-gray-300">
                        <strong>Usage License:</strong> By using amc (AI Music Co-pilot), you are granted a license to generate MIDI patterns.
                        You own the full copyright to any MIDI content you generate using our platform. You are free to use these files in commercial and non-commercial projects royalty-free.
                    </p>
                    <p className="mb-4 text-gray-300">
                        <strong>Disclaimer:</strong> The service is provided "as is". We do not guarantee 100% uptime or that the generated content will meet specific artistic requirements.
                    </p>
                </section>

                {/* Privacy Policy */}
                <section>
                    <h2 className="text-2xl font-semibold mb-4 text-white">2. Privacy Policy</h2>
                    <p className="mb-4 text-gray-300">
                        <strong>Data Collection:</strong> We do not sell your personal data. We collect only necessary information to operate the service (e.g., login credentials if applicable, usage logs for rate limiting).
                    </p>
                    <p className="mb-4 text-gray-300">
                        <strong>Generated Content:</strong> Your generated MIDI files are stored temporarily for download purposes and are not used to train other AI models without your explicit permission.
                    </p>
                </section>

                <div className="pt-8 border-t border-gray-800">
                    <a href="/" className="text-blue-400 hover:text-blue-300 transition-colors">← Back to Generator</a>
                </div>
            </div>
        </div>
    );
}
