import { useState } from 'react';
import './App.css';
import axios from 'axios';

function App() {
  const [formData, setFormData] = useState({
    topic: '',
    slidesNumber: 5,
    gradeLevel: 'High School',
  });
  const [outlines, setOutlines] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };
// Mock generating outlines without API call
// setTimeout(() => {
//   const mockOutlines = [
//     "1. The Water Cycle: Earth's Natural Recycling System",
//     "2. Evaporation in Action: From Oceans to Atmosphere",
//     "3. Cloud Formation: Condensation and Atmospheric Dynamics",
//     "4. Precipitation Patterns: Regional Variations and Climate Impact",
//     "5. Groundwater Systems: The Invisible Reservoir"
//   ];
  
//   setOutlines(mockOutlines);
//   setIsGenerating(false);
// }, 1500);
  
const handleSubmit = (e) => {
    e.preventDefault();
    setIsGenerating(true);
    
    const response = axios.post('http://localhost:8000/generate-outlines', formData)
      .then((response) => {
        setOutlines(response.data.outlines);
        setIsGenerating(false);
      })
      .catch((error) => {
        console.error('Error generating outlines:', error);
        setIsGenerating(false);
      });
    
    return response;
  };

  return (
    <div className="app-container">
      <header>
        <h1>Presentation Generator</h1>
        <p>Create engaging educational presentation in seconds</p>
      </header>

      <main>
        <section className="form-section">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="topic">Presentation Topic:</label>
              <input
                type="text"
                id="topic"
                name="topic"
                value={formData.topic}
                onChange={handleChange}
                placeholder="e.g., The Water Cycle"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="slidesNumber">Number of Slides:</label>
              <input
                type="number"
                id="slidesNumber"
                name="slidesNumber"
                min="3"
                max="20"
                value={formData.slidesNumber}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="gradeLevel">Grade Level:</label>
              <select
                id="gradeLevel"
                name="gradeLevel"
                value={formData.gradeLevel}
                onChange={handleChange}
                required
              >
                <option value="Elementary School">Elementary School</option>
                <option value="Middle School">Middle School</option>
                <option value="High School">High School</option>
                <option value="College">College</option>
              </select>
            </div>

            <button type="submit" disabled={isGenerating} className="submit-btn">
              {isGenerating ? 'Generating...' : 'Generate Outline'}
            </button>
          </form>
        </section>

        <section className="results-section">
          <h2>Your Presentation Outline</h2>
          {outlines.length > 0 ? (
            <div className="outline-container">
              <ul className="outline-list">
                {outlines.map((outline, index) => (
                  <li key={index} className="outline-item">
                    {outline}
                  </li>
                ))}
              </ul>
              <div className="outline-actions">
                <button className="action-btn">
                  Save Outline
                </button>
                <button className="action-btn">
                  Export as PDF
                </button>
              </div>
            </div>
          ) : (
            <p className="no-results">
              {isGenerating 
                ? 'Creating your outline...' 
                : 'Enter your topic details and click "Generate Outline" to create a presentation outline.'}
            </p>
          )}
        </section>
      </main>

      <footer>
        <p>Presentation Outline Generator &copy; {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}

export default App;