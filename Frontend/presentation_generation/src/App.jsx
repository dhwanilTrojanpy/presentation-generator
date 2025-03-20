import { useState } from "react";
import "./App.css";
import axios from "axios";
import OutlineHandler from "./components/OutlineHandler";
import InputHandler from "./components/InputHandler";
import { useRef } from 'react';

function App() {
  const fileInputRef = useRef(null);
  const [formData, setFormData] = useState({
    topic: "",
    slidesNumber: 0,
    gradeLevel: "HIGHSCHOOL",
    file: null
  });
  const [outlines, setOutlines] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleChange = (e) => {
    console.log("formdata",e.target);
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleFileChange = (e) => {
    console.log("formdata",e.target);
    setFormData({
      ...formData,
      file: fileInputRef.current.files[0] || null 
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsGenerating(true);
    console.log("formdata",formData);
    console.log("file",fileInputRef.current.files[0]);
    const form = new FormData();
    form.append("context", formData.topic);
    form.append("numberOfSlides", String(formData.slidesNumber));
    form.append("gradeLevel", formData.gradeLevel);
    if (formData.file) {
      form.append("file", formData.file);
    }
    
    axios
      .post("http://localhost:8000/generate-outline", form, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      .then((response) => {
        console.log("response",response);
        setIsGenerating(false);
        setOutlines(response.data.outlines);
        console.log("outlines",outlines);
      })
      .catch((error) => {
        console.error("Error generating outlines:", error);
        setIsGenerating(false);
      });
    // return response;
  };

  return (
    <div className="app-container">
      <header>
        <h1>Presentation Generator</h1>
        <p>Create engaging educational presentation in seconds</p>
      </header>

      <main>
        <section className="form-section">
          <InputHandler 
          handleSubmit={handleSubmit}
          handleChange={handleChange}
          formData={formData}
          isGenerating={isGenerating}
          handleFileChange={handleFileChange}
          fileInputRef={fileInputRef} />
        </section>

        <section className="results-section">
          <OutlineHandler 
          outlines={outlines}
          isGenerating={isGenerating}  
          setOutlines={setOutlines}
          / >
        </section>
      </main>

      <footer>
        <p>Presentation Outline Generator &copy; {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}

export default App;