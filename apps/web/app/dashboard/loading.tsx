export default function DashboardRouteLoading() {
  return (
    <main className="mx-auto min-h-screen max-w-6xl animate-pulse px-6 py-20" aria-label="Loading dashboard">
      <div className="h-10 w-44 rounded-xl bg-ink/10" />
      <div className="mt-24 h-16 max-w-2xl rounded-2xl bg-ink/10" />
      <div className="mt-12 grid gap-5 md:grid-cols-2">
        <div className="h-52 rounded-[2rem] bg-white/65" />
        <div className="h-52 rounded-[2rem] bg-white/65" />
      </div>
    </main>
  );
}
