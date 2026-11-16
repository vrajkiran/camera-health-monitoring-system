import React, { useState, useRef, useMemo } from 'react';
import { TopologyData, TopologyNode } from '../../types/topology';

interface TopologyGraphProps {
  data: TopologyData;
  onHoverNode: (info: { node: TopologyNode; x: number; y: number } | null) => void;
  onSelectNode: (node: TopologyNode) => void;
}

interface LayoutNode extends TopologyNode {
  x: number;
  y: number;
  radius: number;
}

export const TopologyGraph: React.FC<TopologyGraphProps> = ({
  data,
  onHoverNode,
  onSelectNode,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [selectedLayer, setSelectedLayer] = useState<'ALL' | 'SWITCHES' | 'CAMERAS'>('ALL');

  // Compute hierarchical layout coordinates for all nodes
  const { layoutNodes, layoutEdges, width, height } = useMemo(() => {
    const rawNodes = data.nodes || [];
    const rawEdges = data.edges || [];

    const switchNodes = rawNodes.filter((n) => n.type === 'switch');
    const cameraNodes = rawNodes.filter((n) => n.type === 'camera');

    const totalSwitches = Math.max(1, switchNodes.length);
    const canvasWidth = Math.max(1000, totalSwitches * 220);
    const canvasHeight = 620;

    const nodesMap = new Map<string, LayoutNode>();

    // Root Core Node positioned at top center
    const coreX = canvasWidth / 2;
    const coreY = 80;
    const coreNode: LayoutNode = {
      id: 'CORE-BACKBONE',
      type: 'switch',
      name: 'Campus Core Switch',
      ip_address: '10.0.0.1',
      status: 'ONLINE',
      level: 'core',
      total_cameras: cameraNodes.length,
      offline_cameras: cameraNodes.filter((c) => c.status === 'OFFLINE').length,
      x: coreX,
      y: coreY,
      radius: 28,
    };
    nodesMap.set(coreNode.id, coreNode);

    // Distribution / Edge Switches placed in row 2
    const switchY = 240;
    const switchSpacing = canvasWidth / (totalSwitches + 1);
    switchNodes.forEach((sw, idx) => {
      const sx = switchSpacing * (idx + 1);
      nodesMap.set(sw.id, {
        ...sw,
        level: 'distribution',
        x: sx,
        y: switchY,
        radius: 22,
      });
    });

    // Camera Nodes placed below their parent switch
    const camerasBySwitch = new Map<string, TopologyNode[]>();
    cameraNodes.forEach((cam) => {
      const swId = cam.switch_id || 'UNKNOWN';
      const list = camerasBySwitch.get(swId) || [];
      list.push(cam);
      camerasBySwitch.set(swId, list);
    });

    camerasBySwitch.forEach((cams, swId) => {
      const parent = nodesMap.get(swId);
      const px = parent ? parent.x : canvasWidth / 2;
      const count = cams.length;
      const camSpacing = Math.min(65, (switchSpacing * 0.9) / Math.max(1, count));
      const startX = px - ((count - 1) * camSpacing) / 2;

      cams.forEach((cam, cIdx) => {
        // Stagger rows slightly for dense packing
        const rowOffset = (cIdx % 2) * 50;
        nodesMap.set(cam.id, {
          ...cam,
          x: startX + cIdx * camSpacing,
          y: 420 + rowOffset,
          radius: 14,
        });
      });
    });

    // Build edges with coordinates
    const edgesList: { id: string; x1: number; y1: number; x2: number; y2: number; health: string }[] = [];

    // Core to Switch Edges
    switchNodes.forEach((sw) => {
      const target = nodesMap.get(sw.id);
      if (target) {
        edgesList.push({
          id: `core-${sw.id}`,
          x1: coreX,
          y1: coreY,
          x2: target.x,
          y2: target.y,
          health: sw.status === 'OFFLINE' ? 'DOWN' : 'GOOD',
        });
      }
    });

    // Switch to Camera Edges
    rawEdges.forEach((edge, idx) => {
      const source = nodesMap.get(edge.source);
      const target = nodesMap.get(edge.target);
      if (source && target) {
        edgesList.push({
          id: `edge-${idx}-${edge.source}-${edge.target}`,
          x1: source.x,
          y1: source.y,
          x2: target.x,
          y2: target.y,
          health: edge.health,
        });
      }
    });

    return {
      layoutNodes: Array.from(nodesMap.values()),
      layoutEdges: edgesList,
      width: canvasWidth,
      height: canvasHeight,
    };
  }, [data]);

  // Handle Drag / Pan
  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    setPan({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y,
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleZoom = (delta: number) => {
    setZoom((prev) => Math.min(2.5, Math.max(0.4, prev + delta)));
  };

  const handleReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  return (
    <div className="relative w-full rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-900 overflow-hidden shadow-inner">
      {/* Topology Control Toolbar */}
      <div className="absolute top-4 left-4 z-20 flex flex-wrap items-center gap-2 bg-slate-900/80 backdrop-blur-md p-1.5 rounded-xl border border-slate-700/60 shadow-lg text-xs">
        <div className="flex items-center gap-1 border-r border-slate-700 pr-2">
          <button
            type="button"
            onClick={() => setSelectedLayer('ALL')}
            className={`px-2.5 py-1 rounded-lg font-medium transition-colors ${
              selectedLayer === 'ALL'
                ? 'bg-blue-600 text-white'
                : 'text-slate-300 hover:bg-slate-800'
            }`}
          >
            All Layers
          </button>
          <button
            type="button"
            onClick={() => setSelectedLayer('SWITCHES')}
            className={`px-2.5 py-1 rounded-lg font-medium transition-colors ${
              selectedLayer === 'SWITCHES'
                ? 'bg-blue-600 text-white'
                : 'text-slate-300 hover:bg-slate-800'
            }`}
          >
            Switches Only
          </button>
          <button
            type="button"
            onClick={() => setSelectedLayer('CAMERAS')}
            className={`px-2.5 py-1 rounded-lg font-medium transition-colors ${
              selectedLayer === 'CAMERAS'
                ? 'bg-blue-600 text-white'
                : 'text-slate-300 hover:bg-slate-800'
            }`}
          >
            Cameras
          </button>
        </div>

        {/* Zoom controls */}
        <div className="flex items-center gap-1">
          <button
            type="button"
            title="Zoom In"
            onClick={() => handleZoom(0.2)}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-300 hover:bg-slate-800 hover:text-white"
          >
            <span className="material-symbols-outlined text-[16px]">add</span>
          </button>
          <button
            type="button"
            title="Zoom Out"
            onClick={() => handleZoom(-0.2)}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-300 hover:bg-slate-800 hover:text-white"
          >
            <span className="material-symbols-outlined text-[16px]">remove</span>
          </button>
          <button
            type="button"
            title="Reset View"
            onClick={handleReset}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-300 hover:bg-slate-800 hover:text-white"
          >
            <span className="material-symbols-outlined text-[16px]">center_focus_strong</span>
          </button>
          <span className="text-[11px] font-mono text-slate-400 pl-1">
            {Math.round(zoom * 100)}%
          </span>
        </div>
      </div>

      {/* Legend Badge */}
      <div className="absolute top-4 right-4 z-20 hidden sm:flex items-center gap-3 bg-slate-900/80 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-700/60 shadow-lg text-[11px] text-slate-300">
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
          Good
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
          Degraded
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
          Offline
        </span>
      </div>

      {/* Hi-DPI Responsive Vector SVG Canvas (ISSUE-12) */}
      <div
        ref={containerRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        className={`w-full h-[580px] overflow-hidden select-none cursor-${isDragging ? 'grabbing' : 'grab'}`}
      >
        <svg
          className="w-full h-full"
          viewBox={`0 0 ${width} ${height}`}
          preserveAspectRatio="xMidYMid meet"
        >
          <defs>
            {/* Background Blueprint Grid */}
            <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
              <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#1e293b" strokeWidth="0.8" />
            </pattern>
            {/* Glow filters for status nodes */}
            <filter id="glow-emerald" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            <filter id="glow-rose" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="5" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Grid Background */}
          <rect width="100%" height="100%" fill="url(#grid)" />

          {/* Transform Layer for Pan & Zoom */}
          <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
            {/* Cable Links (Smooth Bezier Curves) */}
            {layoutEdges.map((edge) => {
              if (selectedLayer === 'SWITCHES' && edge.id.startsWith('edge-')) return null;

              const midY = (edge.y1 + edge.y2) / 2;
              const pathD = `M ${edge.x1} ${edge.y1} C ${edge.x1} ${midY}, ${edge.x2} ${midY}, ${edge.x2} ${edge.y2}`;
              const strokeColor =
                edge.health === 'DOWN'
                  ? '#f43f5e'
                  : edge.health === 'DEGRADED'
                  ? '#f59e0b'
                  : '#10b981';

              return (
                <path
                  key={edge.id}
                  d={pathD}
                  fill="none"
                  stroke={strokeColor}
                  strokeWidth={edge.id.startsWith('core-') ? '2.5' : '1.5'}
                  strokeDasharray={edge.health === 'DOWN' ? '4 4' : undefined}
                  opacity={edge.health === 'DOWN' ? 0.7 : 0.85}
                />
              );
            })}

            {/* Topology Nodes */}
            {layoutNodes.map((node) => {
              if (selectedLayer === 'SWITCHES' && node.type === 'camera') return null;
              if (selectedLayer === 'CAMERAS' && node.type === 'switch' && node.id !== 'CORE-BACKBONE') return null;

              const isSwitch = node.type === 'switch';
              const isOffline = node.status === 'OFFLINE';
              const isDegraded = node.status === 'UNSTABLE' || node.status === 'STREAM_FAILURE';

              const fillColor = isSwitch
                ? '#1e293b'
                : isOffline
                ? '#881337'
                : isDegraded
                ? '#78350f'
                : '#064e3b';

              const strokeColor = isOffline
                ? '#f43f5e'
                : isDegraded
                ? '#f59e0b'
                : '#10b981';

              return (
                <g
                  key={node.id}
                  transform={`translate(${node.x}, ${node.y})`}
                  className="cursor-pointer transition-transform duration-100 hover:scale-110"
                  onClick={() => onSelectNode(node)}
                  onMouseEnter={(e) => {
                    const rect = containerRef.current?.getBoundingClientRect();
                    if (rect) {
                      onHoverNode({
                        node,
                        x: e.clientX - rect.left,
                        y: e.clientY - rect.top,
                      });
                    }
                  }}
                  onMouseLeave={() => onHoverNode(null)}
                >
                  {/* Outer Pulsing Aura on Faults */}
                  {isOffline && (
                    <circle
                      r={node.radius + 6}
                      fill="none"
                      stroke="#f43f5e"
                      strokeWidth="2"
                      opacity="0.5"
                      className="animate-ping"
                    />
                  )}

                  {/* Node Circle */}
                  <circle
                    r={node.radius}
                    fill={fillColor}
                    stroke={strokeColor}
                    strokeWidth={isSwitch ? 2.5 : 1.8}
                    filter={isOffline ? 'url(#glow-rose)' : 'url(#glow-emerald)'}
                  />

                  {/* Icon or Text glyph */}
                  <text
                    textAnchor="middle"
                    dy="0.35em"
                    fontSize={isSwitch ? '12px' : '9px'}
                    fontWeight="bold"
                    fill="#ffffff"
                    fontFamily="monospace"
                  >
                    {isSwitch ? (node.id === 'CORE-BACKBONE' ? 'CORE' : 'SW') : 'CAM'}
                  </text>

                  {/* Node Label Below */}
                  <text
                    y={node.radius + 14}
                    textAnchor="middle"
                    fontSize="11px"
                    fontWeight="600"
                    fill="#cbd5e1"
                  >
                    {isSwitch ? node.id : node.name || node.id}
                  </text>

                  {/* Subtext IP address */}
                  <text
                    y={node.radius + 25}
                    textAnchor="middle"
                    fontSize="9px"
                    fill="#94a3b8"
                    fontFamily="monospace"
                  >
                    {node.ip_address || node.switch_ip || ''}
                  </text>
                </g>
              );
            })}
          </g>
        </svg>
      </div>
    </div>
  );
};
