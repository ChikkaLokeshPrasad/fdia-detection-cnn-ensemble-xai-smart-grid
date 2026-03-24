import React from "react"

// IEEE 13-bus feeder physical layout positions
const BUSES = [
  { id: 1,  x: 280, y: 30  },
  { id: 2,  x: 160, y: 90  },
  { id: 3,  x: 400, y: 90  },
  { id: 4,  x: 80,  y: 160 },
  { id: 5,  x: 220, y: 160 },
  { id: 6,  x: 340, y: 160 },
  { id: 7,  x: 480, y: 160 },
  { id: 8,  x: 40,  y: 250 },
  { id: 9,  x: 160, y: 250 },
  { id: 10, x: 280, y: 250 },
  { id: 11, x: 420, y: 250 },
  { id: 12, x: 120, y: 340 },
  { id: 13, x: 320, y: 340 },
]

const EDGES = [
  [1, 2], [1, 3],
  [2, 4], [2, 5],
  [3, 6], [3, 7],
  [4, 8], [5, 9],
  [6, 10],[7, 11],
  [9, 12],[10, 13],
]

// ─── Precise Zone → Physical Bus Mapping ─────────────────────────────────────
// Derived from:
//   23 measurement nodes distributed across 13 physical buses
//   Buses 1-10 have 2 measurement nodes each, buses 11-13 have 1 each
//   define_zones(23) produces 7 zones of measurement nodes
//   Each zone maps to the physical buses whose nodes fall in that zone
//
// Zone 0: nodes [0,1,2,3]   → Bus 1 (nodes 0-1), Bus 2 (nodes 2-3)
// Zone 1: nodes [4,5,6,7]   → Bus 3 (nodes 4-5), Bus 4 (nodes 6-7)
// Zone 2: nodes [8,9,10]    → Bus 5 (nodes 8-9), Bus 6 (node 10)
// Zone 3: nodes [11,12,13]  → Bus 6 (node 11),   Bus 7 (nodes 12-13)
// Zone 4: nodes [14,15,16]  → Bus 8 (nodes 14-15), Bus 9 (node 16)
// Zone 5: nodes [17,18,19]  → Bus 9 (node 17),   Bus 10 (nodes 18-19)
// Zone 6: nodes [20,21,22]  → Bus 11 (node 20),  Bus 12 (node 21), Bus 13 (node 22)

const ZONE_BUSES = {
  0: [1, 2],
  1: [3, 4],
  2: [5, 6],
  3: [6, 7],
  4: [8, 9],
  5: [9, 10],
  6: [11, 12, 13],
}

// Zone label descriptions for the info panel
const ZONE_INFO = {
  0: "Buses 1–2  ·  Nodes 0–3",
  1: "Buses 3–4  ·  Nodes 4–7",
  2: "Buses 5–6  ·  Nodes 8–10",
  3: "Buses 6–7  ·  Nodes 11–13",
  4: "Buses 8–9  ·  Nodes 14–16",
  5: "Buses 9–10 ·  Nodes 17–19",
  6: "Buses 11–13 · Nodes 20–22",
}

function GridVisualization({ data }) {

  const predictedZone = data?.predicted_zone ?? -1
  const isAttack      = (data?.attack_probability || 0) >= 0.5

  const attackedBuses = new Set(
    predictedZone >= 0 && isAttack
      ? (ZONE_BUSES[predictedZone] || [])
      : []
  )

  const W = 540, H = 390

  return (
    <div className="panel">
      <div className="panel-label amber">Power Grid Topology — IEEE 13-Bus</div>

      <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{ display: "block" }}>

        {/* Background grid */}
        {[60,120,180,240,300,360].map(y => (
          <line key={y} x1={0} y1={y} x2={W} y2={y}
            stroke="rgba(0,180,255,0.04)" strokeWidth="1" />
        ))}
        {[100,200,300,400,500].map(x => (
          <line key={x} x1={x} y1={0} x2={x} y2={H}
            stroke="rgba(0,180,255,0.04)" strokeWidth="1" />
        ))}

        {/* Edges */}
        {EDGES.map(([a, b], i) => {
          const busA = BUSES[a - 1]
          const busB = BUSES[b - 1]
          const highlighted = attackedBuses.has(a) || attackedBuses.has(b)
          return (
            <line key={i}
              x1={busA.x} y1={busA.y}
              x2={busB.x} y2={busB.y}
              stroke={highlighted ? "rgba(255,61,61,0.5)" : "rgba(0,200,255,0.18)"}
              strokeWidth={highlighted ? 2 : 1.5}
              strokeDasharray={highlighted ? "6 3" : "none"}
            />
          )
        })}

        {/* Bus nodes */}
        {BUSES.map(bus => {
          const attacked = attackedBuses.has(bus.id)
          return (
            <g key={bus.id}>
              {attacked && (
                <circle cx={bus.x} cy={bus.y} r={18}
                  fill="none"
                  stroke="rgba(255,61,61,0.35)"
                  strokeWidth="1.5"
                  style={{ animation: "pulse-ring 1.4s ease-out infinite" }}
                />
              )}
              <circle cx={bus.x} cy={bus.y} r={13}
                fill={attacked ? "rgba(255,61,61,0.08)" : "rgba(0,200,255,0.05)"}
                stroke={attacked ? "var(--red)" : "rgba(0,200,255,0.3)"}
                strokeWidth="1"
              />
              <circle cx={bus.x} cy={bus.y} r={8}
                fill={attacked ? "#200808" : "#050e18"}
                stroke={attacked ? "var(--red)" : "var(--cyan)"}
                strokeWidth={attacked ? 1.5 : 1}
                style={{
                  filter: attacked
                    ? "drop-shadow(0 0 5px var(--red))"
                    : "drop-shadow(0 0 3px rgba(0,200,255,0.5))"
                }}
              />
              <text x={bus.x} y={bus.y + 4}
                textAnchor="middle"
                fill={attacked ? "var(--red)" : "var(--cyan)"}
                fontSize="8" fontFamily="var(--font-mono)" fontWeight="bold"
              >
                {bus.id}
              </text>
              <text x={bus.x} y={bus.y - 17}
                textAnchor="middle"
                fill={attacked ? "rgba(255,61,61,0.7)" : "rgba(0,200,255,0.35)"}
                fontSize="7" fontFamily="var(--font-mono)"
              >
                B{bus.id}
              </text>
            </g>
          )
        })}
      </svg>

      {/* Zone info + legend */}
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        marginTop: 12, paddingTop: 12,
        borderTop: "1px solid var(--border)"
      }}>
        <div style={{ display: "flex", gap: 18 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{
              display: "inline-block", width: 8, height: 8,
              borderRadius: "50%", background: "var(--cyan)",
              boxShadow: "0 0 4px var(--cyan)"
            }} />
            <span style={{
              fontFamily: "var(--font-label)", fontSize: 10,
              letterSpacing: 1.5, textTransform: "uppercase",
              color: "var(--text-secondary)"
            }}>Normal</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{
              display: "inline-block", width: 8, height: 8,
              borderRadius: "50%", background: "var(--red)",
              boxShadow: "0 0 4px var(--red)"
            }} />
            <span style={{
              fontFamily: "var(--font-label)", fontSize: 10,
              letterSpacing: 1.5, textTransform: "uppercase",
              color: "var(--text-secondary)"
            }}>Attacked</span>
          </div>
        </div>

        {/* Zone detail */}
        {predictedZone >= 0 && isAttack ? (
          <div style={{ textAlign: "right" }}>
            <div className="status-badge attack" style={{ fontSize: 10, marginBottom: 4 }}>
              <span className="dot" />
              Zone {predictedZone} Compromised
            </div>
            <div style={{
              fontFamily: "var(--font-mono)", fontSize: 10,
              color: "var(--text-secondary)"
            }}>
              {ZONE_INFO[predictedZone]}
            </div>
          </div>
        ) : (
          <div style={{
            fontFamily: "var(--font-mono)", fontSize: 10,
            color: "var(--text-muted)"
          }}>
            7 zones · 23 measurement nodes · 13 physical buses
          </div>
        )}
      </div>
    </div>
  )
}

export default GridVisualization