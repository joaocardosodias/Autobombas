import { CameraCard } from "../CameraCard";

export function CameraGrid() {

  const cameras = [
    { id: 1, name: "Câmera Principal", location: "Visão Frontal", status: "online", feedUrl: "http://172.20.10.4/stream" },
    {
      id: 2,
      name: "Câmera 2",
      location: "Visão Lateral Esq.",
      status: "offline",
    },
    {
      id: 3,
      name: "Câmera 3",
      location: "Visão Lateral Dir.",
      status: "offline",
    },
    { id: 4, name: "Câmera 4", location: "Visão Inferior", status: "offline" },
  ];

  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {cameras.map((camera) => (
          <CameraCard
            key={camera.id}
            {...camera}
          />
        ))}
      </div>
    </>
  );
}
