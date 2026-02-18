import React, { useState } from 'react';

const InnovationLab = () => {
    const [problem, setProblem] = useState('');
    const [roadmap, setRoadmap] = useState('');
    const [loading, setLoading] = useState(false);

    const handleGenerate = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/tools/problem-to-project', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ problem_description: problem }),
            });
            const data = await response.json();
            setRoadmap(data.roadmap);
        } catch (error) {
            console.error("Error:", error);
        }
        setLoading(false);
    };

    return (
        <div className="innovation-container">
            <h3>🚀 Problem-to-Project Converter</h3>
            <p>Enter a social problem to get a technical roadmap.</p>
            <textarea 
                className="problem-textarea"
                value={problem}
                onChange={(e) => setProblem(e.target.value)}
                placeholder="Ex: How to help rural students access tech tutorials without internet?"
            />
            <button className="generate-btn" onClick={handleGenerate} disabled={loading}>
                {loading ? "Analyzing..." : "Generate Social Innovation Project"}
            </button>
            {roadmap && <div className="roadmap-display">{roadmap}</div>}
        </div>
    );
};

export default InnovationLab;