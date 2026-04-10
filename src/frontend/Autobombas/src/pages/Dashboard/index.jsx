import { DashboardHeader } from "@/components/DashboardHeader";
import { StatusIndicator } from "@/components/DashboardStatus";
import { SideBar } from "@/components/Sidebar";
import { useState } from "react";
import { DephControl } from "@/components/DephControl";
import { AmperageMeter } from "@/components/AmperageMeter";
import { DirectionalControl } from "@/components/DirectionalControl";
import { SensorsPanel } from "@/components/SensorsPanel";
import { CameraGrid } from "@/components/CameraGrid";
import { useAmperagem } from "@/hooks/useAmperagem";
import { useProfundidade } from "@/hooks/useProfundidade";
import { useMovimentacaoXY } from "@/hooks/useMovimentacao";
import { useDashboardMonitor } from "@/hooks/useDashboardMonitor";
import { useModoAutomatico } from "@/hooks/useModoAutomatico";

//Dados mockados da v0 depois precisa conectar o backend
const DEMO_CAMERAS = [
  {
    id: 1,
    name: "Câmera 1",
    location: "Visão Frontal",
    status: "recording",
    feedUrl: undefined,
  },
  {
    id: 2,
    name: "Câmera 2",
    location: "Visão Lateral Esq.",
    status: "online",
    feedUrl: undefined,
  },
  {
    id: 3,
    name: "Câmera 3",
    location: "Visão Lateral Dir.",
    status: "online",
    feedUrl: undefined,
  },
  {
    id: 4,
    name: "Câmera 4",
    location: "Visão Inferior",
    status: "online",
    feedUrl: undefined,
  },
];

export function Dashboard() {
  const [isSensorOpen, setIsSensorOpen] = useState(false);
  const [isPowerOn, setIsPowerOn] = useState(false);
  const {sensorsList, isSystemOnline, lastUpdated, activeSensorsCount} = useDashboardMonitor();
  const { corrente_a } = useAmperagem(isSystemOnline);
  const { posicao_cm, comprimento_corda_cm, deslocar, isMoving} = useProfundidade()
  const { mover, parar, alternarEnergia} = useMovimentacaoXY()
  const { statusAuto, toggleAuto} = useModoAutomatico();
  const isManualDisable = isMoving || statusAuto.ativo;
  

  const handleClickClose = () => {
    setIsSensorOpen(false);
  };

  const onDeslocar = (cm) => deslocar(cm)

  const handleTogglePower = async () => {
    const novoEstado = !isPowerOn
    const sucesso = await alternarEnergia(novoEstado)
    if (sucesso) setIsPowerOn(novoEstado)
  }
  
  const onMoveForward = () => {
    mover("frente")
  } 

  const onMoveBackward = () => {
    mover("tras")
  } 

  const onMoveLeft = () => {
    mover("esquerda")
  }

  const onMoveRight = () => {
    mover("direita")
  }



  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <SideBar
        onSensorsClick={() => setIsSensorOpen(true)}
        systemStatusCount={`${activeSensorsCount} sensores ativos`}
        isOnline={isSystemOnline}
      />
      <main className="flex-1 flex flex-col min-h-0">
        <DashboardHeader
          statusSlot={<StatusIndicator status={isSystemOnline ? "connected" : "disconnected"} />}
          title="Dashboard de controle"
        />
        <div className="flex-1 overflow-auto p-6">
          {/* Cameras */}
          <section className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-semibold text-primary">
                  Monitoramento de Câmeras
                </h2>
                <p className="text-sm text-muted-foreground">
                  Visualização em tempo real
                </p>
              </div>
              <div className="flex items-center gap-2 text-xs bg-green-500/10 text-green-600 px-3 py-1.5 rounded-full ">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                {DEMO_CAMERAS.lenght} câmeras ativas
              </div>
            </div>
            <CameraGrid cameras={DEMO_CAMERAS} />
          </section>
          {/* Controles */}
          <div className="mb-6 flex flex-col sm:flex-row sm:items-center border-green-700 justify-between gap-4 bg-card p-4 rounded-xl border shadow-sm">
            <div>
              <h2 className="text-lg font-semibold flex items-center gap-3">
                <span className="text-primary">Painel de controle</span>
                <span className={`text-xs px-2.5 py-0.5 rounded-full font-medium ${
                  statusAuto.ativo 
                    ? 'bg-green-100 text-green-600 ' 
                    : 'bg-muted text-muted-foreground border border-border'
                }`}>
                  {statusAuto.ativo ? `Automático (${statusAuto.fase})` : "Manual"}
                </span>
              </h2>
              <p className="text-sm text-muted-foreground mt-1">
                Controles operacionais do sistema
              </p>
            </div>

            {/* Chave de alternância Auto/Manual */}
            <div className="flex bg-muted p-1 rounded-lg shrink-0">
              <button
                onClick={() => toggleAuto(false)}
                className={`px-6 py-2 rounded-md text-sm font-semibold transition-all ${
                  !statusAuto.ativo 
                    ? "bg-background shadow-sm text-foreground" 
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Manual
              </button>
              <button
                onClick={() => toggleAuto(true)}
                className={`px-6 py-2 rounded-md text-sm font-semibold transition-all ${
                  statusAuto.ativo 
                    ? "bg-[#234a2b] text-white shadow-md" 
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Automático
              </button>
            </div>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-stretch">
            <DephControl
              depth_cm={posicao_cm}
              maxDepth={comprimento_corda_cm}
              onDeslocar={onDeslocar}
              isMoving={isManualDisable}
            />

            <AmperageMeter 
            currentValue={corrente_a} 
            maxValue={100} 
            />

            <DirectionalControl
              onForward={onMoveForward}
              onBackward={onMoveBackward}
              onLeft={onMoveLeft}
              onRight={onMoveRight}
              onStop={parar}
              isPowerOn={isPowerOn}
              onTogglePower={handleTogglePower}
            />
          </div>
        </div>
      </main>
      <SensorsPanel
        isOpen={isSensorOpen}
        onClickClose={handleClickClose}
        sensors={sensorsList}
        lastUpdated={lastUpdated}
      />
    </div>
  );
}
