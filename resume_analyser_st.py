import streamlit as st
from wyge.prebuilt_agents.resume_analyser import ResumeAnalyzer
import pandas as pd

def main():
    st.title("Resume ATS Analysis")
    st.subheader("Compare multiple resumes against a job description")

    api_key = st.text_input("Enter your OpenAI API key:", type="password")
    if not api_key:
        st.warning("Please enter your OpenAI API key.")
        return
    
    # Initialize analyzer
    analyzer = ResumeAnalyzer(api_key)

    # Job description input
    st.subheader("Job Description")
    job_description = st.text_area(
        "Enter the job description",
        height=200,
        placeholder="Paste the job description here..."
    )

    # Multiple resume upload
    st.subheader("Upload Resumes")
    uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)
    
    # Display count of uploaded files
    if uploaded_files:
        st.write(f"📄 {len(uploaded_files)} resume(s) uploaded")

    if st.button("Analyze Resumes", key='analyze') and uploaded_files and job_description:
        if len(uploaded_files) == 1:
            # Single resume analysis
            try:
                with st.spinner("Analyzing resume..."):
                    # Extract text from the resume
                    resume_text = analyzer.extract_text_from_pdf(uploaded_files[0])
                    
                    # Analyze the resume
                    result = analyzer.analyze_resume(resume_text, job_description)
                    
                    if isinstance(result, dict) and "JD Match" in result:
                        # Display results
                        st.success("Analysis completed!")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Job Description Match", result["JD Match"])
                        
                        with col2:
                            st.subheader("Missing Keywords")
                            if result["MissingKeywords"]:
                                for keyword in result["MissingKeywords"]:
                                    st.write("•", keyword)
                            else:
                                st.write("No missing keywords found")
                        
                        st.subheader("Profile Summary")
                        st.info(result["Profile Summary"])
                        
                        st.subheader("Suggestions")
                        for suggestion in result["Suggestions"]:
                            st.warning("• " + suggestion)
                    else:
                        st.error("Invalid response format from the analyzer")
                    
            except Exception as e:
                st.error(f"Error occurred: {str(e)}")
                st.error("Please try again with a different resume or job description")
        else:
            # Multiple resume analysis
            try:
                with st.spinner(f"Analyzing {len(uploaded_files)} resumes... This may take a while."):
                    # Prepare resume files for batch processing
                    resume_files = [(file.name, file) for file in uploaded_files]
                    
                    # Analyze multiple resumes
                    results = analyzer.analyze_multiple_resumes(resume_files, job_description)
                    
                    if results:
                        st.success(f"Successfully analyzed {len(results)} resumes!")
                        
                        # Create a summary table
                        summary_data = []
                        for i, result in enumerate(results):
                            summary_data.append({
                                "Rank": i + 1,
                                "Resume": result.get("filename", "Unknown"),
                                "Match %": result.get("JD Match", "0%"),
                                "Missing Keywords": ", ".join(result.get("MissingKeywords", [])) if result.get("MissingKeywords") else "None"
                            })
                        
                        # Display summary table
                        st.subheader("Resume Ranking")
                        df = pd.DataFrame(summary_data)
                        st.dataframe(df, use_container_width=True)
                        
                        # Detailed results in expandable sections
                        st.subheader("Detailed Analysis")
                        for i, result in enumerate(results):
                            with st.expander(f"#{i+1}: {result.get('filename', 'Unknown')} - {result.get('JD Match', '0%')} Match"):
                                st.subheader("Profile Summary")
                                st.info(result.get("Profile Summary", "No summary available"))
                                
                                st.subheader("Missing Keywords")
                                if result.get("MissingKeywords"):
                                    for keyword in result.get("MissingKeywords"):
                                        st.write("•", keyword)
                                else:
                                    st.write("No missing keywords found")
                                
                                st.subheader("Suggestions")
                                for suggestion in result.get("Suggestions", []):
                                    st.warning("• " + suggestion)
                    else:
                        st.error("Failed to analyze resumes. Please try again.")
                        
            except Exception as e:
                st.error(f"Error occurred: {str(e)}")
                st.error("Please try again with different resumes or job description")
    
    else:
        st.warning("Please upload at least one resume and provide a job description.")

if __name__ == "__main__":
    main()