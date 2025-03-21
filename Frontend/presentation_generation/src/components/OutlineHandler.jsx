import React from "react";
import { useState } from "react";
import axios from "axios";
function OutlineHandler({ setOutlines, outlines, isGenerating }) {
  const [EditingIndex, setEditingindex] = useState(null);
  const [slideContents, setSlideContents] = useState([]);

  const handlenewOutline = (e, index) => {
    const newOutlines = [...outlines];
    console.log("TextContent", e);
    newOutlines[index] = e.target.innerHTML;
    setOutlines(newOutlines);
  };
  const handleEdit = (index) => {
    setEditingindex(EditingIndex === index ? null : index);
  };
  const handleSaveOutlines = (outlines) => {
    console.log("outlines", outlines);
    axios.post("http://localhost:8000/geneate-presentation", {
      outlines: outlines,
    });
  };
  return (
    <div>
      <h2>Your Presentation Outline</h2>
      {outlines.length > 0 ? (
        <div className="outline-container">
          <ul className="outline-list">
            {outlines.map((outline, index) => (
              <li type="text" key={index} className="outline-item">
                <div className="outline-edit-container">
                  <div
                    className="outline-edit"
                    onBlur={(e) => handlenewOutline(e, index)}
                    contentEditable={EditingIndex === index}
                  >
                    {outline}
                  </div>
                  <button
                    type="button"
                    className="btn btn-sm btn-primary"
                    onClick={() => handleEdit(index)}
                  >
                    {EditingIndex === index ? "Click to save" : "Click to Edit"}
                  </button>
                </div>
              </li>
            ))}
          </ul>
          <div className="outline-actions">
            <button
              className="action-btn"
              onClick={async () => {
                try {
                  const response = await axios.post("http://localhost:8000/generate-presentation", {
                    outlines: outlines
                  });
                  
                  if (response.data.slides) {
                    setSlideContents(response.data.slides);
                  }
                } catch (error) {
                  console.error("Error generating presentation:", error);
                }
              }}
            >
              Generate Presentation
            </button>
          </div>
          {slideContents.length > 0 && (
            <div className="presentation-slides">
              <h3>Generated Presentation Content</h3>
              {slideContents.map((content, index) => {
                let slideData;
                try {
                  // Remove markdown formatting if present
                  const cleanContent = content.replace(/```json\n|\n```/g, '').trim();
                  slideData = JSON.parse(cleanContent);
                } catch (error) {
                  console.error("Failed to parse JSON:", error);
                  slideData = { error: "Failed to parse slide content" };
                }
                return (
                  <div key={index} className="slide-preview">
                    <h4>Slide {index + 1}: {outlines[index]}</h4>
                    <pre className="slide-content">
                      {JSON.stringify(slideData, null, 2)}
                    </pre>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      ) : (
        <p className="no-results">
          {isGenerating
            ? "Creating your outline..."
            : "You can edit the generated outlines and make ready for your presentation."}
        </p>
      )}
    </div>
  );
}

export default OutlineHandler;
