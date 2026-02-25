const BASE_URL = "http://127.0.0.1:8000";

export async function createSession(studentId) {
  const response = await fetch(`${BASE_URL}/advising-session`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      student_id_number: studentId,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to create session");
  }

  return response.json();
}

export async function uploadTranscript(sessionId, rows) {
  const response = await fetch(
    `http://127.0.0.1:8000/advising-session/${sessionId}/transcript`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(rows),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to upload transcript");
  }

  return response.json();
}

export async function getRecommendations(sessionId, payload) {
  const response = await fetch(
    `http://127.0.0.1:8000/advising-session/${sessionId}/recommendations`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to get recommendations");
  }

  return response.json();
}

export const getGraduationAudit = async (sessionId) => {
  const res = await fetch(
    `http://127.0.0.1:8000/advising-session/${sessionId}/graduation-audit`
  );

  if (!res.ok) {
    throw new Error("Failed to fetch graduation audit");
  }

  return await res.json();
};

// ----------------------------
// Admin - Get Courses
// ----------------------------
export const getAllCourses = async () => {
  const res = await fetch("http://127.0.0.1:8000/admin/courses");

  if (!res.ok) throw new Error("Failed to fetch courses");

  return await res.json();
};

// ----------------------------
// Admin - Create Course
// ----------------------------
export const createCourse = async (data) => {
  const res = await fetch("http://127.0.0.1:8000/admin/courses", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) throw new Error("Failed to create course");

  return await res.json();
};

// ----------------------------
// Admin - Update Course
// ----------------------------
export const updateCourse = async (id, data) => {
  const res = await fetch(
    `http://127.0.0.1:8000/admin/courses/${id}`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }
  );

  if (!res.ok) throw new Error("Failed to update course");

  return await res.json();
};