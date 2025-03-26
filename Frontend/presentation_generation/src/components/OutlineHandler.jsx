import React from "react";
import { useState } from "react";
import axios from "axios";
function OutlineHandler({ setOutlines, outlines, isGenerating }) {
  const [EditingIndex, setEditingindex] = useState(null);
  const [slideContents, setSlideContents] = useState([]);
  const [isGeneratingSlides, setIsGeneratingSlides] = useState(false);
  const [finalResponse, setFinalresponse] = useState("");
  const handlenewOutline = (e, index) => {
    const newOutlines = [...outlines];
    console.log("TextContent", e);
    newOutlines[index] = e.target.innerHTML;
    setOutlines(newOutlines);
  };
  const handleEdit = (index) => {
    setEditingindex(EditingIndex === index ? null : index);
  };

  const generatePresentation = async () => {
    try {
      console.log("Generating presentation with slides:", slideContents);
      await axios.post("http://localhost:8000/generate-presentation", {
        slides: slideContents
      }).then((response) => {
        setFinalresponse(response.message);
      });
      
    } catch (error) {
      console.error("Error generating presentation:", error.response?.data || error.message);
    }
  }
  const generateSlideContent = async () => {
    try {
      setIsGeneratingSlides(true);
      const response = await axios.post(
        "http://localhost:8000/generate-slide-content",
        {
          outlines: outlines,
        },
      );
      if (response.data && response.data.slides) {
        console.log("slideContents", response.data.slides);
        setSlideContents(response.data.slides);
      } else {
        console.error("Invalid response format:", response.data);
      }
    } catch (error) {
      console.error(
        "Error generating presentation:",
        error.response?.data?.detail || error.message,
      );
    } finally {
      setIsGeneratingSlides(false);
    }
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
              onClick={generateSlideContent}
              disabled={isGeneratingSlides}
            >
              {isGeneratingSlides ? "Generating..." : "Generate Slide Content"}
            </button>
          </div>
          {slideContents.length > 0 && (
            <div className="presentation-slides">
              <h3>Generated Presentation Content</h3>
              {slideContents.map((content, index) => {
                return (
                  <div key={index} className="slide-preview">
                    <h4>
                      {outlines[index]}
                    </h4>
                    <pre className="slide-content">
                      {JSON.stringify(content, null, 2)}
                    </pre>
                  </div>
                );
              })}
               <button
          className="action-btn"
            onClick={() => generatePresentation()}
            >
            Generate Presentation
          </button>
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
