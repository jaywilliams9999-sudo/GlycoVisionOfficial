// Display details for the model features.
// The backend's /models endpoint supplies each feature's name and valid range.
// This file adds the human-readable parts. A feature that isn't listed here still
// works: its snake_case name is tidied up and it is shown as a number box.

export const MODEL_INFO = {
  "clinical-v1": { name: "Clinical", blurb: "Uses clinical and lab measurements." },
  "screening-v1": {
    name: "Screening",
    blurb: "Uses health history and lifestyle answers. No lab values needed.",
  },
};

export const modelName = (version) => MODEL_INFO[version]?.name ?? version;

export const LABELS = {
  // clinical-v1
  pregnancies: "Pregnancies",
  glucose: "Glucose",
  blood_pressure: "Diastolic blood pressure",
  skin_thickness: "Triceps skin-fold thickness",
  insulin: "Insulin",
  bmi: "BMI",
  diabetes_pedigree: "Diabetes pedigree function",
  age: "Age",
  // screening-v1
  high_bp: "High blood pressure",
  high_chol: "High cholesterol",
  chol_check: "Cholesterol check in the last 5 years",
  smoker: "Has smoked at least 100 cigarettes",
  stroke: "Has had a stroke",
  heart_disease: "Coronary heart disease or heart attack",
  phys_activity: "Physical activity in the past 30 days",
  fruits: "Eats fruit daily",
  veggies: "Eats vegetables daily",
  heavy_alcohol: "Heavy alcohol use",
  general_health: "General health",
  mental_health_days: "Poor mental health days, past 30",
  physical_health_days: "Poor physical health days, past 30",
  diff_walk: "Serious difficulty walking or climbing stairs",
  sex: "Sex",
  age_group: "Age group",
};

export const UNITS = {
  glucose: "mg/dL",
  blood_pressure: "mm Hg",
  skin_thickness: "mm",
  insulin: "µIU/mL",
  bmi: "kg/m²",
  age: "years",
  mental_health_days: "days",
  physical_health_days: "days",
};

// Shown under a field. These describe how the model's training data measured each value,
// so staff enter the same kind of measurement the model learned from.
export const HINTS = {
  glucose: "Plasma glucose 2 hours into an oral glucose tolerance test.",
  blood_pressure: "Diastolic pressure.",
  insulin: "Serum insulin 2 hours into the same test.",
  diabetes_pedigree: "Score for family history of diabetes.",
  heavy_alcohol: "More than 14 drinks a week for men, or more than 7 for women.",
};

// Fields that are picked from a list instead of typed.
export const CHOICES = {
  general_health: [
    [1, "Excellent"],
    [2, "Very good"],
    [3, "Good"],
    [4, "Fair"],
    [5, "Poor"],
  ],
  sex: [
    [0, "Female"],
    [1, "Male"],
  ],
  age_group: [
    [1, "18 to 24"],
    [2, "25 to 29"],
    [3, "30 to 34"],
    [4, "35 to 39"],
    [5, "40 to 44"],
    [6, "45 to 49"],
    [7, "50 to 54"],
    [8, "55 to 59"],
    [9, "60 to 64"],
    [10, "65 to 69"],
    [11, "70 to 74"],
    [12, "75 to 79"],
    [13, "80 or older"],
  ],
};

export function labelFor(feature) {
  return LABELS[feature] ?? feature.replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase());
}

// A list of [value, text] pairs, or null when the field is a number box.
// Any feature whose valid range is exactly 0 to 1 is treated as Yes/No.
export function choicesFor(feature, spec) {
  if (CHOICES[feature]) return CHOICES[feature];
  if (spec && spec.min === 0 && spec.max === 1) {
    return [
      [1, "Yes"],
      [0, "No"],
    ];
  }
  return null;
}

export function displayValue(feature, value, spec) {
  if (value === null || value === undefined) return "Not measured";
  const choice = choicesFor(feature, spec)?.find(([v]) => v === value);
  if (choice) return choice[1];
  return UNITS[feature] ? `${value} ${UNITS[feature]}` : String(value);
}

export const LEVELS = { low: "Low risk", moderate: "Moderate risk", high: "High risk" };

// The backend stores times in UTC, but SQLite hands them back without a "Z",
// which would make the browser read them as local time. Treat them as UTC.
export function parseDate(s) {
  return new Date(/(Z|[+-]\d\d:?\d\d)$/.test(s) ? s : `${s}Z`);
}

export function formatDateTime(s) {
  return parseDate(s).toLocaleString([], { dateStyle: "medium", timeStyle: "short" });
}

// "1970-05-12" -> a local date. Built from parts so time zones can't shift the day.
export function formatDob(dob) {
  const [y, m, d] = dob.split("-").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString([], { dateStyle: "medium" });
}

export function ageFromDob(dob, today = new Date()) {
  const [y, m, d] = dob.split("-").map(Number);
  let age = today.getFullYear() - y;
  const month = today.getMonth() + 1;
  if (month < m || (month === m && today.getDate() < d)) age -= 1;
  return age;
}

// The screening model uses 5-year bands: 1 = 18-24, 2 = 25-29, ... 13 = 80 or older.
export function ageGroupFor(age) {
  if (age < 18) return null;
  if (age <= 24) return 1;
  return Math.min(13, Math.floor((age - 25) / 5) + 2);
}

// Starting values for the form, taken from the patient's date of birth.
export function defaultsFor(patient) {
  const age = ageFromDob(patient.date_of_birth);
  const out = {};
  if (age >= 18 && age <= 120) {
    out.age = String(age);
    out.age_group = String(ageGroupFor(age));
  }
  return out;
}
