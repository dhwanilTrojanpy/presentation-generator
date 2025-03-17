import React from 'react'
// import { useState } from "react";

function InputHandler({ handleSubmit, handleChange, isGenerating, formData, handleFileChange,fileInputRef }) {
  return (
    <div>
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
            <label htmlFor="file">Upload File (optional):</label>
                <input
                    type="file"
                    id="file"
                    name="file"
                    // value={formData.file}
                    ref={fileInputRef}
                    onChange={handleFileChange}
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
                <option value="PHD">Phd</option>
                <option value="HIGHSCHOOL">High School</option>
                <option value="COLLEGE">College</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={isGenerating}
              className="submit-btn"
            >
              {isGenerating ? "Generating..." : "Generate Outline"}
            </button>
          </form>
    </div>
  )
}

export default InputHandler
