  import { Monitor, Gauge, Navigation, Zap, Thermometer, Droplet } from "lucide-react"
  import { SideBar } from "../../components/Sidebar"
  import { DashboardHeader } from "../../components/DashboardHeader"
  import { PumpInfoCard } from "../../components/SobreInfoCard"
  import { SystemFeatures } from "../../components/SobreSystemFeatures"
  import { TutorialAccordion } from "../../components/SobreTutorial"
  import { SafetyWarnings, SupportCard } from "../../components/SobreSafetySupport"

// ---------------------------------------------------------------------------
// DADOS DE EXEMPLO — substitua por chamadas ao seu backend
// ---------------------------------------------------------------------------

const DEMO_PUMP = {
  id:               "ITB-DRG-2026-G06",
  modelo:           "G06 - AutoBombas POC",
  serie:            "SN-T16G06",
  versaoFirmware:   "v1.0",
  dataInstalacao:   "02/02/2026",
  ultimaManutencao: "10/04/2026",
  capacidade:       "---",
  profundidadeMax:  "35cm",
  potencia:         "75 kW",
  tensao:           "0-0,33mA / 3.3V",
  status:           "online",
}

const DEMO_FEATURES = [
  { id: 1, icon: <Monitor size={20} />,    title: "Monitoramento em Tempo Real", description: "Visualize todas as câmeras e sensores simultaneamente com atualizações instantâneas." },
  { id: 2, icon: <Gauge size={20} />,      title: "Controle de Profundidade",    description: "Ajuste preciso da profundidade da bomba com feedback visual imediato." },
  { id: 3, icon: <Navigation size={20} />, title: "Movimentação Direcional",     description: "Controle completo de movimentação em 4 direções com parada de emergência." },
  { id: 4, icon: <Zap size={20} />,        title: "Monitoramento Elétrico",      description: "Acompanhe o consumo de energia em tempo real para evitar sobrecargas." },
  { id: 5, icon: <Thermometer size={20} />,title: "Sensores Térmicos",           description: "Monitoramento da temperatura do motor e componentes críticos." },
  { id: 6, icon: <Droplet size={20} />,    title: "Sensor de Vazão",             description: "Medição precisa do volume de água sendo bombeado." },
]

const DEMO_TUTORIALS = [
  {
    id: "controles",
    title: "Controles de Movimentação",
    icon: <Navigation size={20} />,
    steps: [
      { title: "Controles Direcionais",  description: "Use os botões de seta para movimentar a bomba horizontalmente. O botão central (pausa) interrompe o movimento atual." },
      { title: "Controle de Profundidade", description: "Os botões de seta para cima e para baixo controlam a subida e descida da bomba. O indicador mostra a profundidade atual em metros." },
      { title: "Parada de Emergência",   description: "O botão de pausa (central) pode ser usado como parada rápida em qualquer situação." },
    ],
  },
  {
    id: "cameras",
    title: "Monitoramento de Câmeras",
    icon: <Monitor size={20} />,
    steps: [
      { title: "Visualização em Grid",   description: "O dashboard exibe 4 câmeras simultaneamente para monitoramento completo da operação." },
      { title: "Expandir Câmera",        description: "Clique no ícone de expansão no canto superior direito de cada câmera para visualização em tela cheia." },
      { title: "Indicadores de Status",  description: "O ponto vermelho indica gravação ativa. Câmeras offline mostram indicador cinza." },
    ],
  },
  {
    id: "sensores",
    title: "Painel de Sensores",
    icon: <Gauge size={20} />,
    steps: [
      { title: "Acessando Sensores",     description: "Clique em 'Sensores' no menu lateral para abrir o painel com todos os sensores conectados." },
      { title: "Status dos Componentes", description: "Verde indica operação normal, amarelo indica alerta, e vermelho indica falha ou offline." },
      { title: "Resumo de Status",       description: "O topo do painel exibe contadores de sensores online, em atenção e offline." },
    ],
  },
  {
    id: "amperagem",
    title: "Medidor de Amperagem",
    icon: <Zap size={20} />,
    steps: [
      { title: "Leitura do Medidor",     description: "O medidor exibe o consumo elétrico atual em Amperes. Valores em verde são normais." },
      { title: "Zonas de Alerta",        description: "Amarelo indica consumo elevado. Vermelho indica sobrecarga — reduza a operação imediatamente." },
      { title: "Monitoramento",          description: "Mantenha o consumo abaixo de 80% da capacidade máxima para operação segura." },
    ],
  },
]

const DEMO_WARNINGS = [
  "Sempre monitore os indicadores de amperagem durante a operação.",
  "Não exceda a profundidade máxima recomendada pelo fabricante.",
  "Em caso de alerta vermelho, interrompa a operação imediatamente.",
  "Realize manutenção preventiva conforme cronograma estabelecido.",
]

// ---------------------------------------------------------------------------
// SobrePage
//
// Props disponíveis:
//   pump          {object}   — dados do equipamento (veja DEMO_PUMP)
//   features      {Array}    — funcionalidades do sistema (veja DEMO_FEATURES)
//   tutorials     {Array}    — tutoriais expansíveis (veja DEMO_TUTORIALS)
//   warnings      {Array}    — lista de strings com avisos de segurança
//   supportPhone  {string}   — telefone do suporte técnico
//   supportEmail  {string}   — e-mail do suporte técnico
//   systemStatus  {"connected"|"disconnected"|"warning"}
//   isOnline      {boolean}  — controla indicador da sidebar
//   onLogout      {Function} — callback: sair
//   onSettings    {Function} — callback: configurações
// ---------------------------------------------------------------------------

export default function SobrePage({
  pump         = DEMO_PUMP,
  features     = DEMO_FEATURES,
  tutorials    = DEMO_TUTORIALS,
  warnings     = DEMO_WARNINGS,
  supportPhone = "(11) 99999-9999",
  supportEmail = "suporte@itubombas.com.br",
  isOnline     = true,
  onLogout     = () => {},
  onSettings   = () => {},
}) {
  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <SideBar
        onSensorsClick={() => {}}
        onSettingsClick={onSettings}
        onLogout={onLogout}
        systemStatusLabel={isOnline ? "Sistema Operacional" : "Sistema Offline"}
        systemStatusCount={pump.versaoFirmware ? `Versão ${pump.versaoFirmware}` : "—"}
        isOnline={isOnline}
      />

      <main className="flex-1 flex flex-col min-h-0">
        <DashboardHeader
          title="Sobre o Sistema"
          subtitle="Informações e tutoriais de utilização"
        />

        <div className="flex-1 overflow-auto p-6">
          <PumpInfoCard pump={pump} />
          <SystemFeatures features={features} />
          <TutorialAccordion tutorials={tutorials} defaultOpen="controles" />
          <SafetyWarnings warnings={warnings} />
          <SupportCard phone={supportPhone} email={supportEmail} />
        </div>
      </main>
    </div>
  )
}
