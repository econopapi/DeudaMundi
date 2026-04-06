import { AppHeader } from "./components/AppHeader";

function App() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl flex-col gap-8 px-6 py-10">
      <AppHeader
        title="DeudaMundi · Global Debt Atlas"
        subtitle="Fase 0: base técnica del atlas interactivo de deuda soberana por país."
      />

      <section className="grid gap-4 rounded-xl border border-slate-800 bg-slate-900/60 p-6 text-slate-300">
        <h2 className="text-xl font-semibold text-slate-100">Próximos pasos del MVP</h2>
        <ul className="list-disc space-y-2 pl-5 text-sm">
          <li>Conectar el endpoint `GET /api/v1/globe-data`.</li>
          <li>Integrar globo 3D con react-three-fiber.</li>
          <li>Agregar vista por país con histórico de deuda.</li>
        </ul>
      </section>
    </main>
  );
}

export default App;
