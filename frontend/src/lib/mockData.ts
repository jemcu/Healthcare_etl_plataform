// Mock data simulating the cleaned clinical dataset (1800 records summarized).
// Replace these arrays with real API calls to your Django/Lovable Cloud backend.

export type Riesgo = "Bajo" | "Medio" | "Alto" | "Crítico";

export interface Paciente {
  id_paciente: number;
  nombres: string;
  apellidos: string;
  edad: number;
  sexo: "M" | "F";
  peso: number;
  altura: number;
  imc: number;
  presion_sistolica: number;
  presion_diastolica: number;
  frecuencia_cardiaca: number;
  glucosa: number;
  colesterol: number;
  saturacion_oxigeno: number;
  temperatura: number;
  fumador: boolean;
  diagnostico_preliminar: string;
  riesgo: Riesgo;
  fecha_consulta: string;
}

const nombres = ["Carlos", "María", "Juan", "Ana", "Luis", "Sofía", "Andrés", "Camila", "Pedro", "Laura", "Diego", "Valentina", "Mateo", "Isabella", "Sebastián"];
const apellidos = ["García", "Rodríguez", "Martínez", "López", "González", "Hernández", "Pérez", "Sánchez", "Ramírez", "Torres", "Flores", "Rivera", "Gómez", "Díaz"];
const diagnosticos = ["Hipertensión", "Diabetes tipo 2", "Obesidad", "Dislipidemia", "Sano", "Asma", "Cardiopatía", "Anemia"];

function rand<T>(arr: T[]) { return arr[Math.floor(Math.random() * arr.length)]; }
function randInt(a: number, b: number) { return Math.floor(Math.random() * (b - a + 1)) + a; }
function randFloat(a: number, b: number, d = 1) { return parseFloat((Math.random() * (b - a) + a).toFixed(d)); }

function clasificarRiesgo(p: Omit<Paciente, "riesgo">): Riesgo {
  let score = 0;
  if (p.presion_sistolica > 140) score += 2;
  if (p.presion_sistolica > 180) score += 2;
  if (p.glucosa > 140) score += 2;
  if (p.glucosa > 300) score += 3;
  if (p.saturacion_oxigeno < 92) score += 2;
  if (p.saturacion_oxigeno < 85) score += 3;
  if (p.imc > 30) score += 1;
  if (p.colesterol > 240) score += 1;
  if (p.fumador) score += 1;
  if (p.edad > 65) score += 1;
  if (score >= 8) return "Crítico";
  if (score >= 5) return "Alto";
  if (score >= 2) return "Medio";
  return "Bajo";
}

export const pacientes: Paciente[] = Array.from({ length: 60 }, (_, i) => {
  const peso = randFloat(45, 120);
  const altura = randFloat(1.5, 1.95, 2);
  const imc = parseFloat((peso / (altura * altura)).toFixed(1));
  const base = {
    id_paciente: 10000 + i,
    nombres: rand(nombres),
    apellidos: `${rand(apellidos)} ${rand(apellidos)}`,
    edad: randInt(18, 85),
    sexo: rand(["M", "F"] as const),
    peso, altura, imc,
    presion_sistolica: randInt(95, 195),
    presion_diastolica: randInt(60, 110),
    frecuencia_cardiaca: randInt(55, 120),
    glucosa: randFloat(70, 320),
    colesterol: randFloat(140, 280),
    saturacion_oxigeno: randFloat(82, 99),
    temperatura: randFloat(35.8, 39.5),
    fumador: Math.random() < 0.3,
    diagnostico_preliminar: rand(diagnosticos),
    fecha_consulta: new Date(Date.now() - randInt(0, 90) * 86400000).toISOString().slice(0, 10),
  };
  return { ...base, riesgo: clasificarRiesgo(base) };
});

export const kpis = {
  totalRegistros: 1800,
  criticos: pacientes.filter(p => p.riesgo === "Crítico").length * 30,
  hipertensos: pacientes.filter(p => p.presion_sistolica > 140).length * 30,
  diabeticos: pacientes.filter(p => p.glucosa > 140).length * 30,
  fumadores: pacientes.filter(p => p.fumador).length * 30,
  imcPromedio: parseFloat((pacientes.reduce((s, p) => s + p.imc, 0) / pacientes.length).toFixed(1)),
};

export const riesgoDistribucion = (["Bajo", "Medio", "Alto", "Crítico"] as Riesgo[]).map(r => ({
  riesgo: r,
  total: pacientes.filter(p => p.riesgo === r).length * 30,
}));

export const tendenciaConsultas = Array.from({ length: 12 }, (_, i) => ({
  mes: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"][i],
  consultas: randInt(80, 250),
  criticos: randInt(5, 40),
}));

export const diagnosticosCount = diagnosticos.map(d => ({
  diagnostico: d,
  cantidad: pacientes.filter(p => p.diagnostico_preliminar === d).length * 30,
}));

export const edadSegmentacion = [
  { rango: "18-30", pacientes: 320 },
  { rango: "31-45", pacientes: 480 },
  { rango: "46-60", pacientes: 520 },
  { rango: "61-75", pacientes: 360 },
  { rango: "76+", pacientes: 120 },
];

export const etlHistorial = [
  { id: 1, fecha: "2026-06-12 09:32", usuario: "admin@ips.com", registros: 1850, validos: 1800, duracion: "12.4s", estado: "Éxito" },
  { id: 2, fecha: "2026-06-11 14:08", usuario: "analista@ips.com", registros: 980, validos: 956, duracion: "7.1s", estado: "Éxito" },
  { id: 3, fecha: "2026-06-10 22:15", usuario: "admin@ips.com", registros: 2200, validos: 2178, duracion: "15.8s", estado: "Éxito" },
  { id: 4, fecha: "2026-06-10 08:44", usuario: "analista@ips.com", registros: 540, validos: 0, duracion: "2.0s", estado: "Error" },
  { id: 5, fecha: "2026-06-09 17:21", usuario: "admin@ips.com", registros: 1620, validos: 1599, duracion: "11.2s", estado: "Éxito" },
];

export const mlMetricas = {
  accuracy: 0.892,
  precision: 0.871,
  recall: 0.854,
  f1: 0.862,
  modelo: "Regresión Logística",
  entrenado: "2026-06-12 10:14",
  matriz: [
    [412, 28, 9, 2],
    [31, 298, 22, 5],
    [11, 19, 187, 14],
    [3, 6, 12, 141],
  ],
};

export const heatmapCorrelacion = [
  { x: "Edad", values: [{ y: "IMC", v: 0.32 }, { y: "Glucosa", v: 0.41 }, { y: "Presión", v: 0.58 }, { y: "Colesterol", v: 0.39 }] },
  { x: "IMC", values: [{ y: "IMC", v: 1.0 }, { y: "Glucosa", v: 0.52 }, { y: "Presión", v: 0.46 }, { y: "Colesterol", v: 0.48 }] },
  { x: "Glucosa", values: [{ y: "IMC", v: 0.52 }, { y: "Glucosa", v: 1.0 }, { y: "Presión", v: 0.61 }, { y: "Colesterol", v: 0.55 }] },
  { x: "Presión", values: [{ y: "IMC", v: 0.46 }, { y: "Glucosa", v: 0.61 }, { y: "Presión", v: 1.0 }, { y: "Colesterol", v: 0.49 }] },
];
