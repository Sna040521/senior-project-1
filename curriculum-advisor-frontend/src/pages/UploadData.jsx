import { useState } from "react";
import { useNavigate } from "react-router-dom";
import * as XLSX from "xlsx";
import { uploadTranscript, getRecommendations } from "../api/api";

function UploadData() {
  const navigate = useNavigate();

  const [transcriptRows, setTranscriptRows] = useState([]);
  const [offeredCourses, setOfferedCourses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // -----------------------------
  // TRANSCRIPT UPLOAD (2 SHEETS)
  // -----------------------------
  const handleTranscriptUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();

    reader.onload = (evt) => {
      const data = new Uint8Array(evt.target.result);
      const workbook = XLSX.read(data, { type: "array" });

      // Sheet 2 = Completed Courses
      const sheet = workbook.Sheets[workbook.SheetNames[1]];
      const json = XLSX.utils.sheet_to_json(sheet);

      // Convert to backend format
      const formatted = json
        .filter((row) => row.Course_Code && row.Grade)
        .map((row) => ({
          course_code: row.Course_Code,
          grade: row.Grade,
          credits_earned: 0, // Backend should calculate
          term: `${row.Semester}/${row.Year}`,
        }));

      setTranscriptRows(formatted);
    };

    reader.readAsArrayBuffer(file);
  };

  // -----------------------------
  // OFFERED COURSES UPLOAD
  // -----------------------------
  const handleOfferedUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();

    reader.onload = (evt) => {
      const data = new Uint8Array(evt.target.result);
      const workbook = XLSX.read(data, { type: "array" });
      const sheet = workbook.Sheets[workbook.SheetNames[0]];
      const json = XLSX.utils.sheet_to_json(sheet);

      const codes = json
        .map((row) => row.course_code || row.Course_Code)
        .filter(Boolean);

      setOfferedCourses(codes);
    };

    reader.readAsArrayBuffer(file);
  };

  // -----------------------------
  // GENERATE RECOMMENDATIONS
  // -----------------------------
  const handleGenerate = async () => {
    try {
      setLoading(true);
      setError("");

      const sessionId = localStorage.getItem("session_id");
      if (!sessionId) throw new Error("Session not found.");

      if (transcriptRows.length === 0)
        throw new Error("Transcript file is required.");

      // Upload transcript
      await uploadTranscript(sessionId, transcriptRows);

      // Get recommendations
      const result = await getRecommendations(sessionId, {
        max_credits: 18,
        offered_courses: offeredCourses,
      });

      localStorage.setItem(
        "recommendation_result",
        JSON.stringify(result)
      );

      navigate("/recommendations");
    } catch (err) {
      console.error(err);
      setError("Something went wrong. Check your files.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h2 style={styles.title}>Upload Academic Data</h2>

        {/* TRANSCRIPT */}
        <div style={styles.section}>
          <label style={styles.label}>
            Upload Transcript (.xlsx – 2 Sheets)
          </label>
          <input
            type="file"
            accept=".xlsx,.xls"
            onChange={handleTranscriptUpload}
          />
        </div>

        {/* TRANSCRIPT PREVIEW */}
        {transcriptRows.length > 0 && (
          <div style={styles.preview}>
            <h4>Transcript Preview</h4>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>Course Code</th>
                  <th style={styles.th}>Grade</th>
                  <th style={styles.th}>Term</th>
                </tr>
              </thead>
              <tbody>
                {transcriptRows.map((row, index) => (
                  <tr
                    key={index}
                    style={{
                    backgroundColor: index % 2 === 0 ? "#ffffff" : "#f9fafb",
                  }}
                  >   
                    <td style={styles.td}>{row.course_code}</td>
                    <td style={styles.td}>{row.grade}</td>
                    <td style={styles.td}>{row.term}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* OFFERED COURSES */}
        <div style={styles.section}>
          <label style={styles.label}>
            Upload Offered Courses (.xlsx)
          </label>
          <input
            type="file"
            accept=".xlsx,.xls"
            onChange={handleOfferedUpload}
          />
        </div>

        {/* OFFERED PREVIEW */}
        {offeredCourses.length > 0 && (
          <div style={styles.preview}>
            <h4>Offered Courses Preview</h4>
            <div style={styles.tagContainer}>
  {offeredCourses.map((code, index) => (
    <span key={index} style={styles.tag}>
      {code}
    </span>
  ))}
</div>
          </div>
        )}

        {/* BUTTON */}
        <button style={styles.button} onClick={handleGenerate}>
          {loading ? "Generating..." : "Generate Recommendations"}
        </button>

        {error && <p style={styles.error}>{error}</p>}
      </div>
    </div>
  );
}

// -----------------------------
// STYLES
// -----------------------------
const styles = {
  page: {
  maxWidth: "1100px",
  margin: "0 auto",
},
  card: {
    backgroundColor: "white",
    padding: "50px",
    borderRadius: "16px",
    width: "900px",
    boxShadow: "0 20px 40px rgba(0,0,0,0.08)",
  },
  title: {
  marginBottom: "35px",
  fontSize: "28px",
  fontWeight: "700",
  textAlign: "left",
},
  section: {
  marginBottom: "30px",
  paddingBottom: "20px",
  borderBottom: "1px solid #e5e7eb",
  },
  label: {
    display: "block",
    marginBottom: "8px",
    fontWeight: "600",
  },
  preview: {
  marginBottom: "30px",
  backgroundColor: "#ffffff",
  padding: "20px",
  borderRadius: "14px",
  border: "1px solid #e5e7eb",
  boxShadow: "0 4px 12px rgba(0,0,0,0.04)",
  maxHeight: "350px",
  overflowY: "auto",
  },
  table: {
  width: "100%",
  borderCollapse: "separate",
  borderSpacing: "0",
  fontSize: "14px",
  },
  button: {
    width: "100%",
    padding: "14px",
    backgroundColor: "#2563eb",
    color: "white",
    border: "none",
    borderRadius: "10px",
    fontSize: "16px",
    fontWeight: "600",
    cursor: "pointer",
  },
  error: {
    marginTop: "20px",
    color: "#dc2626",
  },
  th: {
  textAlign: "left",
  padding: "12px",
  backgroundColor: "#f3f4f6",
  fontWeight: "600",
  fontSize: "13px",
  textTransform: "uppercase",
  letterSpacing: "0.5px",
  position: "sticky",
  top: 0,
  borderBottom: "1px solid #e5e7eb",
},
  td: {
  padding: "12px",
  borderBottom: "1px solid #f1f5f9",
},
tagContainer: {
  display: "flex",
  flexWrap: "wrap",
  gap: "10px",
},

tag: {
  padding: "6px 12px",
  backgroundColor: "#e0e7ff",
  color: "#1e3a8a",
  borderRadius: "20px",
  fontSize: "13px",
  fontWeight: "500",
},
};

export default UploadData;