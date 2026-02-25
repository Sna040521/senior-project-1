import { useEffect, useState } from "react";
import {
  getAllCourses,
  createCourse,
  updateCourse,
} from "../api/api";

function AdminCourses() {
  const [courses, setCourses] = useState([]);
  const [form, setForm] = useState({
    course_name: "",
    credits: 3,
    is_ethics_seminar: false,
    is_active: true,
  });
  const [editingId, setEditingId] = useState(null);

  const loadCourses = async () => {
    const data = await getAllCourses();
    setCourses(data);
  };

  useEffect(() => {
    loadCourses();
  }, []);

  const handleSubmit = async () => {
    if (!form.course_name) return;

    if (editingId) {
      await updateCourse(editingId, form);
      setEditingId(null);
    } else {
      await createCourse(form);
    }

    setForm({
      course_name: "",
      credits: 3,
      is_ethics_seminar: false,
      is_active: true,
    });

    loadCourses();
  };

  const handleEdit = (course) => {
    setForm({
      course_name: course.course_name,
      credits: course.credits,
      is_ethics_seminar: course.is_ethics_seminar,
      is_active: course.is_active,
    });
    setEditingId(course.course_id);
  };

  return (
    <div style={styles.page}>
      <h1 style={styles.pageTitle}>Admin Course Management</h1>

      {/* ================= FORM ================= */}
      <div style={styles.card}>
        <h2 style={styles.sectionTitle}>
          {editingId ? "Edit Course" : "Create New Course"}
        </h2>

        <div style={styles.formGroup}>
          <label style={styles.label}>Course Name</label>
          <input
            style={styles.input}
            placeholder="Enter course name"
            value={form.course_name}
            onChange={(e) =>
              setForm({ ...form, course_name: e.target.value })
            }
          />
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>Credits</label>
          <input
            style={styles.input}
            type="number"
            value={form.credits}
            onChange={(e) =>
              setForm({ ...form, credits: Number(e.target.value) })
            }
          />
        </div>

        <div style={styles.checkboxGroup}>
          <label style={styles.checkboxLabel}>
            <input
              type="checkbox"
              checked={form.is_ethics_seminar}
              onChange={(e) =>
                setForm({
                  ...form,
                  is_ethics_seminar: e.target.checked,
                })
              }
            />
            Ethics Seminar
          </label>

          <label style={styles.checkboxLabel}>
            <input
              type="checkbox"
              checked={form.is_active}
              onChange={(e) =>
                setForm({
                  ...form,
                  is_active: e.target.checked,
                })
              }
            />
            Active
          </label>
        </div>

        <button style={styles.primaryButton} onClick={handleSubmit}>
          {editingId ? "Update Course" : "Create Course"}
        </button>
      </div>

      {/* ================= TABLE ================= */}
      <div style={styles.card}>
        <h2 style={styles.sectionTitle}>All Courses</h2>

        <div style={styles.tableWrapper}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>ID</th>
                <th style={styles.th}>Name</th>
                <th style={styles.th}>Credits</th>
                <th style={styles.th}>Seminar</th>
                <th style={styles.th}>Active</th>
                <th style={styles.th}>Action</th>
              </tr>
            </thead>
            <tbody>
              {courses.map((c, index) => (
                <tr
                  key={c.course_id}
                  style={{
                    backgroundColor:
                      index % 2 === 0 ? "#ffffff" : "#f9fafb",
                  }}
                >
                  <td style={styles.td}>{c.course_id}</td>
                  <td style={styles.td}>{c.course_name}</td>
                  <td style={styles.td}>{c.credits}</td>
                  <td style={styles.td}>
                    {c.is_ethics_seminar ? "Yes" : "No"}
                  </td>
                  <td style={styles.td}>
                    {c.is_active ? "Yes" : "No"}
                  </td>
                  <td style={styles.td}>
                    <button
                      style={styles.editButton}
                      onClick={() => handleEdit(c)}
                    >
                      Edit
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

/* ================= STYLES ================= */

const styles = {
  page: {
    maxWidth: "1200px",
    margin: "0 auto",
  },

  pageTitle: {
    fontSize: "28px",
    fontWeight: "700",
    marginBottom: "35px",
  },

  card: {
    backgroundColor: "white",
    padding: "30px",
    borderRadius: "16px",
    boxShadow: "0 6px 18px rgba(0,0,0,0.06)",
    border: "1px solid #f1f5f9",
    marginBottom: "40px",
  },

  sectionTitle: {
    fontSize: "20px",
    fontWeight: "600",
    marginBottom: "20px",
  },

  formGroup: {
    marginBottom: "20px",
  },

  label: {
    display: "block",
    fontSize: "14px",
    fontWeight: "500",
    marginBottom: "6px",
  },

  input: {
    width: "100%",
    padding: "10px 12px",
    borderRadius: "8px",
    border: "1px solid #d1d5db",
    fontSize: "14px",
  },

  checkboxGroup: {
    display: "flex",
    gap: "20px",
    marginBottom: "20px",
  },

  checkboxLabel: {
    display: "flex",
    alignItems: "center",
    gap: "6px",
    fontSize: "14px",
  },

  primaryButton: {
    padding: "10px 18px",
    backgroundColor: "#2563eb",
    color: "white",
    border: "none",
    borderRadius: "8px",
    fontWeight: "600",
    cursor: "pointer",
  },

  tableWrapper: {
    overflowX: "auto",
  },

  table: {
    width: "100%",
    borderCollapse: "separate",
    borderSpacing: "0",
    fontSize: "14px",
  },

  th: {
    textAlign: "left",
    padding: "14px",
    backgroundColor: "#f3f4f6",
    fontWeight: "600",
    fontSize: "13px",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
    borderBottom: "1px solid #e5e7eb",
  },

  td: {
    padding: "14px",
    borderBottom: "1px solid #f1f5f9",
  },

  editButton: {
    padding: "6px 12px",
    backgroundColor: "#e0e7ff",
    color: "#1e3a8a",
    border: "none",
    borderRadius: "6px",
    fontSize: "13px",
    fontWeight: "500",
    cursor: "pointer",
  },
};

export default AdminCourses;