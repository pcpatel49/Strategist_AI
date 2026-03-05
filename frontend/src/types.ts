export interface StudentProfile {
  student_id: string;
  first_name: string;
  last_name: string;
  email: string;
  current_grade: number | null;
  graduation_year: number | null;
  gpa: number | null;
  sat_score: number | null;
  act_score: number | null;
  target_universities: string[];
  target_majors: string[];
}

export interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  current_grade: number;
  graduation_year: number;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  student_id: string;
}

export interface Course {
  id: number;
  course_name: string;
  course_level: string;
  grade: string | null;
  credits: number | null;
  semester: string | null;
  year: number | null;
}

export interface Activity {
  id: number;
  activity_name: string;
  category: string | null;
  role: string | null;
  hours_per_week: number | null;
  achievements: string[];
}

export interface ChatMessage {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface Milestone {
  id: number;
  semester: string | null;
  title: string;
  description: string | null;
  status: string;
  due_date: string | null;
  completed_at: string | null;
}

export interface StrategicPlan {
  id: number;
  plan_data: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  milestones: Milestone[];
}

export interface DashboardStats {
  profile_completion: number;
  upcoming_milestones: Milestone[];
  recent_activities: Activity[];
  readiness_score: number;
}
