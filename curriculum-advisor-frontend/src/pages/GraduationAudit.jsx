import { useEffect, useState } from "react";
import { getGraduationAudit } from "../api/api";

function GraduationAudit() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const sessionId = localStorage.getItem("session_id");
    if (!sessionId) return;

    getGraduationAudit(sessionId).then(setData);
  }, []);

  if (!data) {
    return (
      <div style={styles.page}>
        <div style={styles.card}>
          <h2>Loading Graduation Audit...</h2>
        </div>
      </div>
    );
  }

  const percent = data.credit_audit.percentage_completed;

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        <h1 style={styles.title}>Graduation Audit Dashboard</h1>

        {/* Overall Credit Progress */}
        <div style={styles.card}>
          <h2>Overall Credit Progress</h2>

          <div style={styles.progressBar}>
            <div
              style={{
                ...styles.progressFill,
                width: `${percent}%`,
              }}
            />
          </div>

          <p>
            {data.credit_audit.earned_credits} /{" "}
            {data.credit_audit.required_credits} Credits Completed (
            {percent}%)
          </p>
        </div>

        {/* Main Category Breakdown */}
        <div style={styles.card}>
          <h2>Main Category Breakdown</h2>
          {data.main_category_audit.map((cat, index) => (
            <div key={index} style={styles.categoryBlock}>
              <h4>{cat.main_category}</h4>
              <p>
                {cat.earned_credits} / {cat.required_credits} Credits
              </p>
            </div>
          ))}
        </div>

        {/* Seminar Status */}
        <div style={styles.card}>
          <h2>Professional Ethics Seminar</h2>
          <p>
            Completed: {data.seminar_audit.completed} /{" "}
            {data.seminar_audit.required_total}
          </p>
          <p>Status: {data.seminar_audit.status}</p>
        </div>

        {/* Graduation Status */}
        <div style={styles.statusCard}>
          <h2>Graduation Status</h2>
          <span
            style={
              data.graduation_status === "ELIGIBLE"
                ? styles.statusGreen
                : styles.statusRed
            }
          >
            {data.graduation_status}
          </span>
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    backgroundColor: "#f4f6f9",
    padding: "40px",
  },
  container: {
    maxWidth: "1000px",
    margin: "0 auto",
  },
  title: {
    marginBottom: "30px",
  },
  card: {
    backgroundColor: "white",
    padding: "30px",
    borderRadius: "12px",
    marginBottom: "30px",
    boxShadow: "0 8px 20px rgba(0,0,0,0.05)",
  },
  progressBar: {
    height: "20px",
    backgroundColor: "#e5e7eb",
    borderRadius: "10px",
    overflow: "hidden",
    marginBottom: "15px",
  },
  progressFill: {
    height: "100%",
    backgroundColor: "#2563eb",
  },
  categoryBlock: {
    marginBottom: "15px",
  },
  statusCard: {
    backgroundColor: "white",
    padding: "30px",
    borderRadius: "12px",
    textAlign: "center",
    boxShadow: "0 8px 20px rgba(0,0,0,0.05)",
  },
  statusGreen: {
    padding: "8px 20px",
    backgroundColor: "#16a34a",
    color: "white",
    borderRadius: "20px",
  },
  statusRed: {
    padding: "8px 20px",
    backgroundColor: "#dc2626",
    color: "white",
    borderRadius: "20px",
  },
};

export default GraduationAudit;