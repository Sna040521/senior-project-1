import { useState } from "react";
import { createSession } from "../api/api";

function CreateSession() {
  const [studentId, setStudentId] = useState("");
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    if (!studentId) return;

    try {
      setLoading(true);
      const res = await createSession(studentId);
      localStorage.setItem("session_id", res.session_id);
      window.location.href = "/upload";
    } catch (err) {
      console.error(err);
      alert("Failed to create session.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.title}>Create Advising Session</h1>
        <p style={styles.subtitle}>
          Enter student ID to begin academic recommendation process.
        </p>

        <div style={styles.formGroup}>
          <label style={styles.label}>Student ID</label>
          <input
            style={styles.input}
            placeholder="e.g. 6531336"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
          />
        </div>

        <button style={styles.button} onClick={handleCreate}>
          {loading ? "Creating..." : "Create Session"}
        </button>
      </div>
    </div>
  );
}

/* ================= STYLES ================= */

const styles = {
  page: {
    minHeight: "100vh",
    background: "linear-gradient(135deg, #eef2ff, #f8fafc)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    padding: "20px",
  },

  card: {
    backgroundColor: "white",
    padding: "60px",
    borderRadius: "20px",
    width: "500px",
    boxShadow: "0 20px 50px rgba(0,0,0,0.08)",
    border: "1px solid #f1f5f9",
  },

  title: {
    fontSize: "28px",
    fontWeight: "700",
    marginBottom: "10px",
  },

  subtitle: {
    fontSize: "14px",
    color: "#6b7280",
    marginBottom: "30px",
  },

  formGroup: {
    marginBottom: "25px",
  },

  label: {
    display: "block",
    fontSize: "14px",
    fontWeight: "500",
    marginBottom: "6px",
  },

  input: {
    width: "100%",
    padding: "12px 14px",
    borderRadius: "10px",
    border: "1px solid #d1d5db",
    fontSize: "14px",
  },

  button: {
    width: "100%",
    padding: "14px",
    backgroundColor: "#2563eb",
    color: "white",
    border: "none",
    borderRadius: "10px",
    fontSize: "15px",
    fontWeight: "600",
    cursor: "pointer",
  },
};

export default CreateSession;