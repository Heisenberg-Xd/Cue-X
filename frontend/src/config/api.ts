const BASE = import.meta.env.VITE_API_BASE;

console.log("🔥 API_BASE =", BASE);  // ADD THIS

if (!BASE) {
  throw new Error("❌ VITE_API_BASE missing in production");
}

export const API_BASE = BASE;