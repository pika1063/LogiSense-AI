import { useEffect, useMemo, useRef, useState } from "react";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const THEMES = {
  midnight: {
    name: "Midnight",
    description: "Deep navy · violet · cyan",
  },
  aurora: {
    name: "Aurora",
    description: "Teal · emerald · violet",
  },
  light: {
    name: "Light",
    description: "Bright interface · dark Earth",
  },
};

const DEFAULT_FORM = {
  days_for_shipment_scheduled: 3,
  shipping_mode: "Standard Class",
  market: "USCA",
  order_region: "West of USA",
  customer_segment: "Consumer",
  customer_state: "CA",
  category_name: "Cleats",
  department_name: "Outdoors",
};



/* ==========================================================
   GLOBE
   ========================================================== */

function GlobeNetwork() {
  return (
    <div className="globe-scene">

      <div className="earth-aura aura-1"></div>
      <div className="earth-aura aura-2"></div>
      <div className="earth-aura aura-3"></div>

      <div className="orbit orbit-1"></div>
      <div className="orbit orbit-2"></div>
      <div className="orbit orbit-3"></div>

      <div className="globe">

        <div className="earth-light"></div>

        <div className="globe-grid latitude latitude-1"></div>
        <div className="globe-grid latitude latitude-2"></div>
        <div className="globe-grid latitude latitude-3"></div>
        <div className="globe-grid latitude latitude-4"></div>

        <div className="globe-grid longitude longitude-1"></div>
        <div className="globe-grid longitude longitude-2"></div>
        <div className="globe-grid longitude longitude-3"></div>
        <div className="globe-grid longitude longitude-4"></div>

        <div className="continent c-1"></div>
        <div className="continent c-2"></div>
        <div className="continent c-3"></div>
        <div className="continent c-4"></div>
        <div className="continent c-5"></div>

        <div className="city-point city-1"></div>
        <div className="city-point city-2"></div>
        <div className="city-point city-3"></div>
        <div className="city-point city-4"></div>
        <div className="city-point city-5"></div>

        <div className="route-line route-a"></div>
        <div className="route-line route-b"></div>
        <div className="route-line route-c"></div>

        <div className="shipment shipment-a"></div>
        <div className="shipment shipment-b"></div>
        <div className="shipment shipment-c"></div>

        <div className="earth-core">
          <span>LS</span>
        </div>

      </div>

      <div className="earth-label earth-label-1">
        <span className="earth-label-dot violet"></span>
        Warehouse
      </div>

      <div className="earth-label earth-label-2">
        <span className="earth-label-dot cyan"></span>
        In transit
      </div>

      <div className="earth-label earth-label-3">
        <span className="earth-label-dot green"></span>
        Customer
      </div>

      <div className="route-text route-text-1">
        ROUTE 01
      </div>

      <div className="route-text route-text-2">
        ROUTE 02
      </div>

    </div>
  );
}


/* ==========================================================
   KPI
   ========================================================== */

function KpiCard({
  icon,
  value,
  label,
  note,
}) {
  return (
    <div className="kpi-card interactive-card">

      <div className="kpi-icon">
        {icon}
      </div>

      <div className="kpi-content">

        <span>{label}</span>

        <strong>{value}</strong>

        <small>{note}</small>

      </div>

    </div>
  );
}


/* ==========================================================
   BAR CHART
   ========================================================== */

function AnalyticsBarChart({
  title,
  subtitle,
  data,
  limit = 6,
}) {
  const [view, setView] = useState("late");

  const chartData = useMemo(() => {

    if (!Array.isArray(data)) {
      return [];
    }

    return [...data]
      .map((item) => ({
        ...item,

        lateRate:
          item.shipments > 0
            ? (
                item.late_shipments /
                item.shipments
              ) * 100
            : 0,
      }))
      .sort(
        (a, b) =>
          b.shipments -
          a.shipments
      )
      .slice(0, limit);

  }, [data, limit]);

  const maxValue =
    view === "late"
      ? Math.max(
          ...chartData.map(
            (item) =>
              item.late_shipments
          ),
          1
        )
      : 100;

  return (
    <div className="analytics-card interactive-card">

      <div className="analytics-card-header">

        <div>

          <span className="section-label">
            ANALYTICS
          </span>

          <h3>{title}</h3>

          <p>{subtitle}</p>

        </div>

        <div className="chart-switch">

          <button
            type="button"
            className={
              view === "late"
                ? "active"
                : ""
            }
            onClick={() =>
              setView("late")
            }
          >
            Volume
          </button>

          <button
            type="button"
            className={
              view === "rate"
                ? "active"
                : ""
            }
            onClick={() =>
              setView("rate")
            }
          >
            Rate
          </button>

        </div>

      </div>


      <div className="bars">

        {chartData.map((item) => {

          const value =
            view === "late"
              ? item.late_shipments
              : item.lateRate;

          const width =
            view === "late"
              ? (value / maxValue) *
                100
              : item.lateRate;

          return (
            <div
              className="bar-row"
              key={item.name}
            >

              <div
                className="bar-name"
                title={item.name}
              >
                {item.name}
              </div>

              <div className="bar-track">

                <div
                  className="bar-fill"
                  style={{
                    width:
                      `${Math.max(
                        width,
                        3
                      )}%`,
                  }}
                ></div>

              </div>

              <div className="bar-number">
                {view === "late"
                  ? value.toLocaleString()
                  : `${value.toFixed(
                      1
                    )}%`}
              </div>

            </div>
          );
        })}

      </div>

    </div>
  );
}


/* ==========================================================
   DONUT
   ========================================================== */

function DonutChart({
  late,
  onTime,
}) {
  const total =
    late + onTime;

  const latePercent =
    total > 0
      ? (late / total) * 100
      : 0;

  return (
    <div className="donut-layout">

      <div
        className="donut-chart"
        style={{
          "--late-angle":
            `${latePercent * 3.6}deg`,
        }}
      >

        <div className="donut-hole">

          <strong>
            {latePercent.toFixed(1)}%
          </strong>

          <span>
            late
          </span>

        </div>

      </div>


      <div className="donut-legend">

        <div className="legend-item">

          <span className="legend-color danger"></span>

          <div>

            <strong>
              {late.toLocaleString()}
            </strong>

            <span>
              Late shipments
            </span>

          </div>

        </div>


        <div className="legend-item">

          <span className="legend-color success"></span>

          <div>

            <strong>
              {onTime.toLocaleString()}
            </strong>

            <span>
              On-time shipments
            </span>

          </div>

        </div>

      </div>

    </div>
  );
}


/* ==========================================================
   THEME PANEL
   ========================================================== */

function ThemePanel({
  theme,
  setTheme,
  open,
  setOpen,
}) {
  return (
    <div className="theme-wrap">

      <button
        type="button"
        className="theme-button"
        onClick={() =>
          setOpen(
            (value) => !value
          )
        }
      >

        <span className="theme-icon">
          ◐
        </span>

        <span>
          Theme
        </span>

        <span className="theme-arrow">
          {open ? "↑" : "↓"}
        </span>

      </button>


      {open && (
        <div className="theme-panel">

          <div className="theme-panel-title">

            <span className="section-label">
              APPEARANCE
            </span>

            <strong>
              Choose a theme
            </strong>

          </div>


          <div className="theme-list">

            {Object.entries(THEMES).map(
              ([key, value]) => (
                <button
                  type="button"
                  key={key}
                  className={`theme-option ${
                    theme === key
                      ? "selected"
                      : ""
                  }`}
                  onClick={() => {
                    setTheme(key);
                    setOpen(false);
                  }}
                >

                  <span
                    className={`theme-swatch swatch-${key}`}
                  ></span>

                  <span className="theme-text">

                    <strong>
                      {value.name}
                    </strong>

                    <small>
                      {value.description}
                    </small>

                  </span>

                  {theme === key && (
                    <span className="theme-selected">
                      ✓
                    </span>
                  )}

                </button>
              )
            )}

          </div>

        </div>
      )}

    </div>
  );
}


/* ==========================================================
   APP
   ========================================================== */

function App() {

  const globeRef = useRef(null);

  const target = useRef({
    x: 18,
    y: 0,
    scale: 1,
  });

  const current = useRef({
    x: 18,
    y: 0,
    scale: 1,
  });


  const [theme, setTheme] =
    useState(
      localStorage.getItem(
        "logisense-theme"
      ) || "midnight"
    );

  const [themeOpen, setThemeOpen] =
    useState(false);


  const [formData, setFormData] =
    useState(DEFAULT_FORM);

  const [result, setResult] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  const [analytics, setAnalytics] =
    useState(null);

  const [analyticsLoading, setAnalyticsLoading] =
    useState(true);


  const [insights, setInsights] =
    useState(null);


  /* ========================================================
     SHIPMENTS
     ======================================================== */

  const [shipments, setShipments] =
    useState([]);

  const [shipmentLoading, setShipmentLoading] =
    useState(true);

  const [shipmentError, setShipmentError] =
    useState("");

  const [shipmentPage, setShipmentPage] =
    useState(0);

  const [shipmentSearch, setShipmentSearch] =
    useState("");

  const SHIPMENT_LIMIT = 12;


  /* ========================================================
     SHIPPING PERFORMANCE
     ======================================================== */

  const [
    shippingPerformance,
    setShippingPerformance,
  ] = useState([]);

  const [
    shippingPerformanceLoading,
    setShippingPerformanceLoading,
  ] = useState(true);


  /* ========================================================
     THEME
     ======================================================== */

  useEffect(() => {

    document.documentElement.dataset.theme =
      theme;

    localStorage.setItem(
      "logisense-theme",
      theme
    );

  }, [theme]);


  /* ========================================================
     EARTH SCROLL MOVEMENT
     ======================================================== */

  useEffect(() => {

    let raf;
    let scrollTimeout;


    const path = [

      {
        progress: 0.00,
        x: 18,
        y: 0,
        scale: 1.00,
      },

      {
        progress: 0.12,
        x: 9,
        y: 2,
        scale: 1.08,
      },

      {
        progress: 0.28,
        x: 3,
        y: 1,
        scale: 1.04,
      },

      {
        progress: 0.45,
        x: 13,
        y: -2,
        scale: 1.02,
      },

      {
        progress: 0.62,
        x: 5,
        y: 3,
        scale: 1.05,
      },

      {
        progress: 0.78,
        x: 14,
        y: 1,
        scale: 1.02,
      },

      {
        progress: 0.90,
        x: 7,
        y: -2,
        scale: 1.04,
      },

      {
        progress: 1.00,
        x: 15,
        y: 1,
        scale: 1.02,
      },

    ];


    const ease = (t) =>
      t * t * (3 - 2 * t);


    const updateTarget = () => {

      const scrollTop =
        window.scrollY;

      const maxScroll = Math.max(
        document.documentElement
          .scrollHeight -
          window.innerHeight,
        1
      );

      const progress = Math.min(
        Math.max(
          scrollTop / maxScroll,
          0
        ),
        1
      );


      let start = path[0];

      let end =
        path[path.length - 1];


      for (
        let i = 0;
        i < path.length - 1;
        i++
      ) {

        if (
          progress >=
            path[i].progress &&
          progress <=
            path[i + 1].progress
        ) {

          start = path[i];
          end = path[i + 1];

          break;
        }

      }


      const range =
        end.progress -
        start.progress;


      const localProgress =
        range === 0
          ? 0
          :
            (
              progress -
              start.progress
            ) /
            range;


      const smooth =
        ease(
          Math.min(
            Math.max(
              localProgress,
              0
            ),
            1
          )
        );


      target.current.x =
        start.x +
        (
          end.x -
          start.x
        ) *
        smooth;

      target.current.y =
        start.y +
        (
          end.y -
          start.y
        ) *
        smooth;

      target.current.scale =
        start.scale +
        (
          end.scale -
          start.scale
        ) *
        smooth;

    };


    const animate = () => {

      current.current.x +=
        (
          target.current.x -
          current.current.x
        ) * 0.055;


      current.current.y +=
        (
          target.current.y -
          current.current.y
        ) * 0.055;


      current.current.scale +=
        (
          target.current.scale -
          current.current.scale
        ) * 0.055;


      if (globeRef.current) {

        globeRef.current.style.transform = `
          translate3d(
            calc(-50% + ${current.current.x}vw),
            calc(-50% + ${current.current.y}vh),
            0
          )
          scale(${current.current.scale})
        `;

      }


      raf =
        requestAnimationFrame(
          animate
        );

    };


    const handleScroll = () => {

      updateTarget();

      clearTimeout(
        scrollTimeout
      );

      scrollTimeout =
        setTimeout(
          updateTarget,
          80
        );

    };


    window.addEventListener(
      "scroll",
      handleScroll,
      {
        passive: true,
      }
    );


    window.addEventListener(
      "resize",
      updateTarget
    );


    updateTarget();


    raf =
      requestAnimationFrame(
        animate
      );


    return () => {

      window.removeEventListener(
        "scroll",
        handleScroll
      );

      window.removeEventListener(
        "resize",
        updateTarget
      );

      clearTimeout(
        scrollTimeout
      );

      cancelAnimationFrame(
        raf
      );

    };

  }, []);


  /* ========================================================
     ANALYTICS
     ======================================================== */

  useEffect(() => {

    const loadAnalytics =
      async () => {

        try {

          const response =
            await fetch(
              `${API_BASE}/analytics`
            );

          if (!response.ok) {
            throw new Error(
              "Analytics unavailable."
            );
          }

          const data =
            await response.json();

          setAnalytics(data);

        } catch (err) {

          console.error(err);

        } finally {

          setAnalyticsLoading(false);

        }

      };

    loadAnalytics();

  }, []);


  /* ========================================================
     INSIGHTS
     ======================================================== */

  useEffect(() => {

    const loadInsights =
      async () => {

        try {

          const response =
            await fetch(
              `${API_BASE}/insights`
            );

          if (!response.ok) {
            return;
          }

          const data =
            await response.json();

          setInsights(data);

        } catch (err) {

          console.error(err);

        }

      };

    loadInsights();

  }, []);


  /* ========================================================
     LOAD SHIPMENTS
     ======================================================== */

  useEffect(() => {

    const loadShipments =
      async () => {

        try {

          setShipmentLoading(
            true
          );

          setShipmentError("");

          const response =
            await fetch(
              `${API_BASE}/shipments?limit=${SHIPMENT_LIMIT}&offset=${shipmentPage * SHIPMENT_LIMIT}`
            );

          if (!response.ok) {

            throw new Error(
              "Unable to load shipments."
            );

          }

          const data =
            await response.json();

          setShipments(
            data.shipments || []
          );

        } catch (err) {

          console.error(err);

          setShipmentError(
            err.message ||
              "Unable to load shipments."
          );

        } finally {

          setShipmentLoading(
            false
          );

        }

      };

    loadShipments();

  }, [shipmentPage]);


  /* ========================================================
     SHIPPING PERFORMANCE
     ======================================================== */

  useEffect(() => {

    const loadShippingPerformance =
      async () => {

        try {

          const response =
            await fetch(
              `${API_BASE}/shipments/by-carrier`
            );

          if (!response.ok) {

            throw new Error(
              "Unable to load shipping performance."
            );

          }

          const data =
            await response.json();

          setShippingPerformance(
            data
          );

        } catch (err) {

          console.error(err);

        } finally {

          setShippingPerformanceLoading(
            false
          );

        }

      };

    loadShippingPerformance();

  }, []);


  /* ========================================================
     NAVIGATION
     ======================================================== */

  const navigateTo = (id) => {

    document
      .getElementById(id)
      ?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });

    setThemeOpen(false);

  };


  /* ========================================================
     PREDICTION
     ======================================================== */

  const handleChange = (
    event
  ) => {

    const {
      name,
      value,
    } = event.target;


    setFormData(
      (current) => ({
        ...current,

        [name]:
          name ===
          "days_for_shipment_scheduled"
            ? Number(value)
            : value,
      })
    );

  };


  const handleSubmit = async (
    event
  ) => {

    event.preventDefault();

    setLoading(true);

    setError("");

    setResult(null);


    try {

      const response =
        await fetch(
          `${API_BASE}/predict`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",

              Accept:
                "application/json",
            },

            body:
              JSON.stringify(
                formData
              ),
          }
        );


      const data =
        await response.json();


      if (!response.ok) {

        throw new Error(
          data.detail ||
            "Prediction failed."
        );

      }


      setResult(data);

    } catch (err) {

      setError(
        err.message ||
          "Unable to connect to the backend."
      );

    } finally {

      setLoading(false);

    }

  };


  /* ========================================================
     SUMMARY DATA
     ======================================================== */

  const totalShipments =
    analytics?.total_shipments ??
    172765;

  const lateShipments =
    analytics?.late_shipments ??
    98977;

  const onTimeShipments =
    analytics?.on_time_shipments ??
    73788;

  const lateRate =
    analytics?.late_rate ??
    57.29;


  /* ========================================================
     FEATURES
     ======================================================== */

  const topFeatures =
    useMemo(() => {

      const source =
        insights?.top_features;


      if (Array.isArray(source)) {

        return source
          .map((item) => ({
            name:
              item.name ??
              item.feature ??
              "Feature",

            importance:
              Number(
                item.importance ??
                  item.Importance ??
                  0
              ),
          }))

          .sort(
            (a, b) =>
              b.importance -
              a.importance
          )

          .slice(0, 6);

      }


      if (
        source &&
        typeof source ===
          "object"
      ) {

        return Object.entries(
          source
        )

          .map(
            ([name, importance]) => ({
              name,

              importance:
                Number(
                  importance
                ),
            })
          )

          .sort(
            (a, b) =>
              b.importance -
              a.importance
          )

          .slice(0, 6);

      }


      return [];

    }, [insights]);


  const maxImportance =
    Math.max(
      ...topFeatures.map(
        (item) =>
          item.importance
      ),
      0.001
    );


  const riskAngle =
    result
      ? Math.min(
          result.delay_probability,
          100
        ) * 3.6
      : 0;


  /* ========================================================
     FILTER SHIPMENTS
     ======================================================== */

  const filteredShipments =
    shipments.filter(
      (shipment) => {

        if (
          !shipmentSearch.trim()
        ) {
          return true;
        }


        const search =
          shipmentSearch
            .toLowerCase();


        return (

          String(
            shipment["Order Id"] ||
              ""
          )
            .toLowerCase()
            .includes(search) ||

          String(
            shipment["Shipping Mode"] ||
              ""
          )
            .toLowerCase()
            .includes(search) ||

          String(
            shipment["Market"] ||
              ""
          )
            .toLowerCase()
            .includes(search) ||

          String(
            shipment["Order Region"] ||
              ""
          )
            .toLowerCase()
            .includes(search) ||

          String(
            shipment["Customer Segment"] ||
              ""
          )
            .toLowerCase()
            .includes(search)

        );

      }
    );


  /* ========================================================
     RETURN
     ======================================================== */

  return (
    <div className="app">

      {/* ====================================================
          BACKGROUND
          ==================================================== */}

      <div className="background-layer">

        <div className="noise"></div>

        <div className="background-grid"></div>

        <div className="ambient ambient-one"></div>

        <div className="ambient ambient-two"></div>

        <div className="particles">

          <span></span>
          <span></span>
          <span></span>
          <span></span>
          <span></span>
          <span></span>
          <span></span>

        </div>

      </div>


      <div className="scroll-progress"></div>


      {/* ====================================================
          GLOBAL EARTH
          ==================================================== */}

      <div
        ref={globeRef}
        className="global-globe"
      >
        <GlobeNetwork />
      </div>


      {/* ====================================================
          HEADER
          ==================================================== */}

      <header className="header">

        <button
          type="button"
          className="brand"
          onClick={() =>
            navigateTo("overview")
          }
        >

          <span className="brand-mark">
            L
          </span>

          <span className="brand-name">
            LogiSense
            <b>-AI</b>
          </span>

        </button>


        <nav className="navigation">

          <button
            type="button"
            onClick={() =>
              navigateTo("overview")
            }
          >
            Overview
          </button>


          <button
            type="button"
            onClick={() =>
              navigateTo("shipments")
            }
          >
            Shipments
          </button>


          <button
            type="button"
            onClick={() =>
              navigateTo("analytics")
            }
          >
            Analytics
          </button>


          <button
            type="button"
            onClick={() =>
              navigateTo("prediction")
            }
          >
            Prediction
          </button>


          <button
            type="button"
            onClick={() =>
              navigateTo("insights")
            }
          >
            Model Insights
          </button>

        </nav>


        <div className="header-right">

          <ThemePanel
            theme={theme}
            setTheme={setTheme}
            open={themeOpen}
            setOpen={setThemeOpen}
          />


          <div className="online-status">

            <span></span>

            System online

          </div>

        </div>

      </header>


      <main className="main">


        {/* ==================================================
            HERO
            ================================================== */}

        <section
          id="overview"
          className="hero"
        >

          <div className="hero-content">

            <div className="hero-kicker">

              <span></span>

              GLOBAL SUPPLY CHAIN INTELLIGENCE

            </div>


            <h1>

              Predict delays.

              <em>
                Prevent disruption.
              </em>

            </h1>


            <p className="hero-description">

              LogiSense-AI turns shipment data
              into predictive delivery intelligence
              so logistics teams can see risk before
              it becomes a delay.

            </p>


            <div className="hero-actions">

              <button
                type="button"
                className="primary-button"
                onClick={() =>
                  navigateTo("prediction")
                }
              >

                Analyze a shipment

                <span>
                  →
                </span>

              </button>


              <button
                type="button"
                className="secondary-button"
                onClick={() =>
                  navigateTo("analytics")
                }
              >

                View analytics

                <span>
                  ↗
                </span>

              </button>

            </div>


            <div className="hero-meta">

              <span>
                <i></i>
                172K+ real records
              </span>

              <span>
                <i></i>
                Leakage-safe features
              </span>

              <span>
                <i></i>
                FastAPI connected
              </span>

            </div>

          </div>


          <div className="hero-empty"></div>

        </section>


        {/* ==================================================
            KPI
            ================================================== */}

        <section className="kpi-section">

          <KpiCard
            icon="◉"
            value={
              totalShipments.toLocaleString()
            }
            label="SHIPMENT RECORDS"
            note="Real delivery observations"
          />


          <KpiCard
            icon="!"
            value={`${lateRate}%`}
            label="LATE RATE"
            note="Observed delay exposure"
          />


          <KpiCard
            icon="✦"
            value="69.08%"
            label="MODEL F1"
            note="Selected XGBoost"
          />


          <KpiCard
            icon="◎"
            value="136"
            label="ML FEATURES"
            note="Encoded model inputs"
          />

        </section>


        {/* ==================================================
            SHIPMENTS
            ================================================== */}

        <section
          id="shipments"
          className="shipments-section"
        >

          <div className="section-heading">

            <div>

              <span className="section-label">
                LIVE SHIPMENT DATABASE
              </span>

              <h2>
                Shipment intelligence.
              </h2>

              <p>
                Real shipment records retrieved directly
                from the LogiSense SQLite database.
              </p>

            </div>


            <div className="data-badge">

              <span></span>

              SQLITE CONNECTED

            </div>

          </div>


          <div className="shipment-toolbar interactive-card">

            <div className="shipment-search">

              <span>
                ⌕
              </span>

              <input
                type="text"
                placeholder="Search visible shipments..."
                value={shipmentSearch}
                onChange={(event) =>
                  setShipmentSearch(
                    event.target.value
                  )
                }
              />

            </div>


            <div className="shipment-info">

              <span>
                Showing
              </span>

              <strong>
                {filteredShipments.length}
              </strong>

              <span>
                records
              </span>

            </div>

          </div>


          <div className="shipment-table-card interactive-card">

            {shipmentLoading ? (

              <div className="shipment-loading">

                <div className="loading-ring"></div>

                Loading shipment records...

              </div>

            ) : shipmentError ? (

              <div className="shipment-error">
                {shipmentError}
              </div>

            ) : (

              <div className="shipment-table-wrap">

                <table className="shipment-table">

                  <thead>

                    <tr>

                      <th>
                        Order
                      </th>

                      <th>
                        Shipping Mode
                      </th>

                      <th>
                        Market
                      </th>

                      <th>
                        Region
                      </th>

                      <th>
                        Customer
                      </th>

                      <th>
                        Scheduled Days
                      </th>

                      <th>
                        Risk
                      </th>

                    </tr>

                  </thead>


                  <tbody>

                    {filteredShipments.map(
                      (
                        shipment,
                        index
                      ) => {

                        const late =
                          Number(
                            shipment[
                              "Late_delivery_risk"
                            ]
                          ) === 1;


                        return (

                          <tr
                            key={
                              shipment[
                                "Order Id"
                              ] ||
                              `${index}-${shipment["Customer Zipcode"]}`
                            }
                          >

                            <td>

                              <span className="order-id">

                                #
                                {shipment[
                                  "Order Id"
                                ] || "—"}

                              </span>

                            </td>


                            <td>

                              <span className="table-mode">

                                {shipment[
                                  "Shipping Mode"
                                ] || "—"}

                              </span>

                            </td>


                            <td>

                              {shipment[
                                "Market"
                              ] || "—"}

                            </td>


                            <td>

                              <span
                                className="table-region"
                                title={
                                  shipment[
                                    "Order Region"
                                  ]
                                }
                              >
                                {
                                  shipment[
                                    "Order Region"
                                  ]
                                }
                              </span>

                            </td>


                            <td>

                              {shipment[
                                "Customer Segment"
                              ] || "—"}

                            </td>


                            <td>

                              <span className="scheduled-days">

                                {
                                  shipment[
                                    "Days for shipment (scheduled)"
                                  ] ?? "—"
                                }{" "}
                                days

                              </span>

                            </td>


                            <td>

                              <span
                                className={`shipment-risk ${
                                  late
                                    ? "late"
                                    : "on-time"
                                }`}
                              >

                                <i></i>

                                {late
                                  ? "Late"
                                  : "On Time"}

                              </span>

                            </td>

                          </tr>

                        );

                      }
                    )}

                  </tbody>

                </table>

              </div>

            )}

          </div>


          <div className="shipment-pagination">

            <button
              type="button"
              disabled={
                shipmentPage === 0
              }
              onClick={() =>
                setShipmentPage(
                  (page) =>
                    Math.max(
                      page - 1,
                      0
                    )
                )
              }
            >
              ← Previous
            </button>


            <span>

              Page{" "}

              <strong>
                {shipmentPage + 1}
              </strong>

            </span>


            <button
              type="button"
              disabled={
                shipments.length <
                SHIPMENT_LIMIT
              }
              onClick={() =>
                setShipmentPage(
                  (page) =>
                    page + 1
                )
              }
            >
              Next →
            </button>

          </div>

        </section>


        {/* ==================================================
            INTRO
            ================================================== */}

        <section className="intro-section">

          <div className="intro-text">

            <span className="section-label">
              THE DECISION LOOP
            </span>

            <h2>

              From shipment data

              <span>
                {" "}to foresight.
              </span>

            </h2>


            <p>

              Instead of waiting for delivery
              problems to appear, LogiSense-AI
              provides an early signal about where
              risk is concentrated.

            </p>

          </div>


          <div className="intro-cards">

            <div className="intro-card interactive-card">

              <span>
                01
              </span>

              <div className="intro-icon">
                ◌
              </div>

              <h3>
                Capture
              </h3>

              <p>
                Use shipment conditions known
                before delivery.
              </p>

            </div>


            <div className="intro-card interactive-card">

              <span>
                02
              </span>

              <div className="intro-icon">
                ✦
              </div>

              <h3>
                Predict
              </h3>

              <p>
                Estimate the probability of
                delivery delay.
              </p>

            </div>


            <div className="intro-card interactive-card">

              <span>
                03
              </span>

              <div className="intro-icon">
                ↗
              </div>

              <h3>
                Act
              </h3>

              <p>
                Prioritize attention before risk
                becomes disruption.
              </p>

            </div>

          </div>

        </section>


        {/* ==================================================
            ANALYTICS
            ================================================== */}

        <section
          id="analytics"
          className="analytics-section"
        >

          <div className="section-heading">

            <div>

              <span className="section-label">
                REAL DATA INTELLIGENCE
              </span>

              <h2>
                See the network.
              </h2>

              <p>
                Real shipment analytics from the
                dataset powering LogiSense-AI.
              </p>

            </div>


            <div className="data-badge">

              <span></span>

              LIVE API DATA

            </div>

          </div>


          {analyticsLoading ? (

            <div className="analytics-loader">

              <div className="loading-ring"></div>

              Loading logistics data...

            </div>

          ) : analytics ? (

            <>

              <div className="analytics-feature-grid">

                <div className="analytics-overview interactive-card">

                  <div className="analytics-card-header">

                    <div>

                      <span className="section-label">
                        DELIVERY OUTCOME
                      </span>

                      <h3>
                        Delivery performance
                      </h3>

                      <p>
                        Distribution of observed
                        shipment outcomes.
                      </p>

                    </div>


                    <span className="mini-count">
                      {totalShipments.toLocaleString()}
                    </span>

                  </div>


                  <DonutChart
                    late={
                      lateShipments
                    }
                    onTime={
                      onTimeShipments
                    }
                  />

                </div>


                <AnalyticsBarChart
                  title="Shipping modes"
                  subtitle="Late-shipment volume by shipping method."
                  data={
                    analytics.shipping_mode
                  }
                  limit={4}
                />

              </div>


              <div className="analytics-grid">

                <AnalyticsBarChart
                  title="Markets"
                  subtitle="Global market comparison."
                  data={
                    analytics.market
                  }
                  limit={5}
                />


                <AnalyticsBarChart
                  title="Customer segments"
                  subtitle="Delay exposure by segment."
                  data={
                    analytics.customer_segment
                  }
                  limit={3}
                />


                <AnalyticsBarChart
                  title="Departments"
                  subtitle="Shipment concentration by department."
                  data={
                    analytics.department_name
                  }
                  limit={7}
                />

              </div>


              <div className="analytics-wide">

                <AnalyticsBarChart
                  title="Order regions"
                  subtitle="Largest operating regions by shipment volume."
                  data={
                    analytics.order_region
                  }
                  limit={10}
                />

              </div>


              {/* ==========================================
                  REGION INTELLIGENCE
                  ========================================== */}

              <div className="region-intelligence">

                <div className="region-intelligence-header">

                  <div>

                    <span className="section-label">
                      REGIONAL RISK
                    </span>

                    <h3>
                      Where delays concentrate
                    </h3>

                    <p>
                      Compare shipment volume and observed
                      delay exposure across operating regions.
                    </p>

                  </div>


                  <div className="region-summary">

                    <span>
                      REGIONS ANALYZED
                    </span>

                    <strong>
                      {analytics?.order_region?.length || 0}
                    </strong>

                  </div>

                </div>


                <div className="region-list">

                  {(analytics?.order_region || [])
                    .slice()
                    .sort(
                      (a, b) =>
                        Number(
                          b.lateRate || 0
                        ) -
                        Number(
                          a.lateRate || 0
                        )
                    )
                    .slice(0, 8)
                    .map(
                      (region, index) => {

                        const risk =
                          Number(
                            region.lateRate ||
                              0
                          );


                        let riskClass =
                          "low";


                        if (
                          risk >=
                          65
                        ) {
                          riskClass =
                            "high";
                        } else if (
                          risk >=
                          50
                        ) {
                          riskClass =
                            "medium";
                        }


                        return (

                          <div
                            className="region-row"
                            key={
                              region.name
                            }
                          >

                            <div className="region-rank">
                              {String(
                                index + 1
                              ).padStart(
                                2,
                                "0"
                              )}
                            </div>


                            <div className="region-main">

                              <div className="region-topline">

                                <strong
                                  title={
                                    region.name
                                  }
                                >
                                  {region.name}
                                </strong>

                                <span
                                  className={`region-risk ${riskClass}`}
                                >
                                  {risk.toFixed(
                                    1
                                  )}
                                  % late
                                </span>

                              </div>


                              <div className="region-progress">

                                <div className="region-progress-track">

                                  <div
                                    className={`region-progress-fill ${riskClass}`}
                                    style={{
                                      width:
                                        `${Math.min(
                                          risk,
                                          100
                                        )}%`,
                                    }}
                                  ></div>

                                </div>

                              </div>

                            </div>


                            <div className="region-volume">

                              <strong>
                                {Number(
                                  region.shipments ||
                                    0
                                ).toLocaleString()}
                              </strong>

                              <span>
                                shipments
                              </span>

                            </div>

                          </div>

                        );

                      }
                    )}

                </div>

              </div>


              {/* ==========================================
                  SHIPPING PERFORMANCE
                  ========================================== */}

              <div className="shipping-performance">

                <div className="shipping-performance-header">

                  <div>

                    <span className="section-label">
                      SHIPPING PERFORMANCE
                    </span>

                    <h3>
                      Which shipping modes carry the most risk?
                    </h3>

                    <p>
                      Compare shipment volume and observed delay
                      rates across available shipping modes.
                    </p>

                  </div>


                  <div className="data-badge">

                    <span></span>

                    REAL DATABASE DATA

                  </div>

                </div>


                {shippingPerformanceLoading ? (

                  <div className="shipment-loading">

                    <div className="loading-ring"></div>

                    Loading shipping performance...

                  </div>

                ) : (

                  <div className="shipping-performance-grid">

                    {shippingPerformance.map(
                      (item) => {

                        const rate =
                          Number(
                            item.late_rate ||
                              0
                          );


                        let riskClass =
                          "low";


                        if (
                          rate >=
                          65
                        ) {
                          riskClass =
                            "high";
                        } else if (
                          rate >=
                          50
                        ) {
                          riskClass =
                            "medium";
                        }


                        return (

                          <div
                            className="shipping-mode-card interactive-card"
                            key={
                              item.carrier
                            }
                          >

                            <div className="shipping-mode-top">

                              <div className="shipping-mode-icon">
                                →
                              </div>

                              <span
                                className={`shipping-mode-risk ${riskClass}`}
                              >
                                {riskClass.toUpperCase()}
                              </span>

                            </div>


                            <h4>
                              {item.carrier}
                            </h4>


                            <div className="shipping-mode-rate">

                              <strong>
                                {rate.toFixed(
                                  2
                                )}
                                %
                              </strong>

                              <span>
                                late rate
                              </span>

                            </div>


                            <div className="shipping-mode-bar">

                              <div
                                className={`shipping-mode-fill ${riskClass}`}
                                style={{
                                  width:
                                    `${Math.min(
                                      rate,
                                      100
                                    )}%`,
                                }}
                              ></div>

                            </div>


                            <div className="shipping-mode-stats">

                              <div>

                                <span>
                                  Shipments
                                </span>

                                <strong>
                                  {Number(
                                    item.shipments ||
                                      0
                                  ).toLocaleString()}
                                </strong>

                              </div>


                              <div>

                                <span>
                                  Late
                                </span>

                                <strong>
                                  {Number(
                                    item.late_shipments ||
                                      0
                                  ).toLocaleString()}
                                </strong>

                              </div>

                            </div>

                          </div>

                        );

                      }
                    )}

                  </div>

                )}

              </div>

            </>

          ) : (

            <div className="analytics-error">
              Analytics could not be loaded.
            </div>

          )}

        </section>


        {/* ==================================================
            PREDICTION
            ================================================== */}

        <section
          id="prediction"
          className="prediction-section"
        >

          <div className="section-heading">

            <div>

              <span className="section-label">
                PREDICTIVE ENGINE
              </span>

              <h2>
                Test a shipment.
              </h2>

              <p>
                Enter pre-delivery information
                and calculate its delay risk.
              </p>

            </div>


            <div className="model-badge">

              <span></span>

              XGBOOST

            </div>

          </div>


          <div className="prediction-grid">

            <div className="prediction-card interactive-card">

              <div className="card-heading">

                <div>

                  <span className="step-label">
                    SHIPMENT PROFILE
                  </span>

                  <h3>
                    Input conditions
                  </h3>

                </div>


                <div className="input-number">
                  08
                </div>

              </div>


              <form
                className="prediction-form"
                onSubmit={
                  handleSubmit
                }
              >

                <div className="form-field">

                  <label>
                    Scheduled shipping days
                  </label>

                  <input
                    type="number"
                    min="0"
                    name="days_for_shipment_scheduled"
                    value={
                      formData.days_for_shipment_scheduled
                    }
                    onChange={
                      handleChange
                    }
                    required
                  />

                </div>


                <div className="form-field">

                  <label>
                    Shipping mode
                  </label>

                  <select
                    name="shipping_mode"
                    value={
                      formData.shipping_mode
                    }
                    onChange={
                      handleChange
                    }
                  >

                    <option>
                      Standard Class
                    </option>

                    <option>
                      Second Class
                    </option>

                    <option>
                      First Class
                    </option>

                    <option>
                      Same Day
                    </option>

                  </select>

                </div>


                <div className="form-field">

                  <label>
                    Market
                  </label>

                  <select
                    name="market"
                    value={
                      formData.market
                    }
                    onChange={
                      handleChange
                    }
                  >

                    <option>
                      USCA
                    </option>

                    <option>
                      LATAM
                    </option>

                    <option>
                      Europe
                    </option>

                    <option>
                      Pacific Asia
                    </option>

                    <option>
                      Africa
                    </option>

                  </select>

                </div>


                <div className="form-field">

                  <label>
                    Order region
                  </label>

                  <input
                    type="text"
                    name="order_region"
                    value={
                      formData.order_region
                    }
                    onChange={
                      handleChange
                    }
                    placeholder="West of USA"
                    required
                  />

                </div>


                <div className="form-field">

                  <label>
                    Customer segment
                  </label>

                  <select
                    name="customer_segment"
                    value={
                      formData.customer_segment
                    }
                    onChange={
                      handleChange
                    }
                  >

                    <option>
                      Consumer
                    </option>

                    <option>
                      Corporate
                    </option>

                    <option>
                      Home Office
                    </option>

                  </select>

                </div>


                <div className="form-field">

                  <label>
                    Customer state
                  </label>

                  <input
                    type="text"
                    name="customer_state"
                    value={
                      formData.customer_state
                    }
                    onChange={
                      handleChange
                    }
                    placeholder="CA"
                    required
                  />

                </div>


                <div className="form-field">

                  <label>
                    Category
                  </label>

                  <input
                    type="text"
                    name="category_name"
                    value={
                      formData.category_name
                    }
                    onChange={
                      handleChange
                    }
                    placeholder="Cleats"
                    required
                  />

                </div>


                <div className="form-field">

                  <label>
                    Department
                  </label>

                  <input
                    type="text"
                    name="department_name"
                    value={
                      formData.department_name
                    }
                    onChange={
                      handleChange
                    }
                    placeholder="Outdoors"
                    required
                  />

                </div>


                <div className="form-footer">

                  <div className="safe-note">

                    <span>
                      ✓
                    </span>

                    Pre-delivery features only

                  </div>


                  <button
                    type="submit"
                    className="predict-button"
                    disabled={loading}
                  >

                    {loading
                      ? "Analyzing..."
                      : "Run prediction"}

                    <span>
                      →
                    </span>

                  </button>

                </div>


                {error && (
                  <div className="form-error">
                    {error}
                  </div>
                )}

              </form>

            </div>


            <div className="prediction-result interactive-card">

              <div className="card-heading">

                <div>

                  <span className="step-label">
                    AI RISK ENGINE
                  </span>

                  <h3>
                    Delivery risk
                  </h3>

                </div>


                <div className="ai-badge">
                  AI
                </div>

              </div>


              {!result ? (

                <div className="empty-result">

                  <div className="radar">

                    <div className="radar-circle radar-1"></div>
                    <div className="radar-circle radar-2"></div>
                    <div className="radar-circle radar-3"></div>

                    <div className="radar-core">
                      LS
                    </div>

                  </div>


                  <h4>
                    Ready to analyze
                  </h4>


                  <p>
                    Run a prediction to see the
                    estimated delay probability.
                  </p>

                </div>

              ) : (

                <div className="live-result">

                  <div
                    className={`risk-dial ${
                      result.risk_level.toLowerCase()
                    }`}
                    style={{
                      "--risk-angle":
                        `${riskAngle}deg`,
                    }}
                  >

                    <div className="risk-dial-content">

                      <strong>
                        {result.delay_probability}%
                      </strong>

                      <span>
                        DELAY RISK
                      </span>

                    </div>

                  </div>


                  <div className="prediction-output">

                    <h4>
                      {result.prediction_label}
                    </h4>


                    <span
                      className={`risk-badge ${
                        result.risk_level.toLowerCase()
                      }`}
                    >

                      <i></i>

                      {result.risk_level} risk

                    </span>

                  </div>


                  <div className="result-stats">

                    <div>

                      <span>
                        Probability
                      </span>

                      <strong>
                        {result.delay_probability}%
                      </strong>

                    </div>


                    <div>

                      <span>
                        Prediction
                      </span>

                      <strong>
                        {result.prediction_label}
                      </strong>

                    </div>


                    <div>

                      <span>
                        Model
                      </span>

                      <strong>
                        XGBOOST
                      </strong>

                    </div>

                  </div>


                  <div className="model-signal">

                    <span>
                      ✦
                    </span>

                    <div>

                      <strong>
                        Model signal
                      </strong>

                      <p>
                        The current shipment profile
                        produces a{" "}
                        <b>
                          {result.delay_probability}%
                        </b>{" "}
                        estimated probability of
                        delivery delay.
                      </p>

                    </div>

                  </div>

                </div>

              )}

            </div>

          </div>

        </section>


        {/* ==================================================
            INSIGHTS
            ================================================== */}

        <section
          id="insights"
          className="insights-section"
        >

          <div className="section-heading">

            <div>

              <span className="section-label">
                EXPLAINABLE ML
              </span>

              <h2>
                Understand the model.
              </h2>

              <p>
                See how the selected model performs
                and which signals matter most.
              </p>

            </div>


            <div className="model-badge">

              <span></span>

               XGBOOST

            </div>

          </div>


          <div className="insights-grid">

            <div className="performance-card interactive-card">

              <div className="card-heading">

                <div>

                  <span className="section-label">
                    PERFORMANCE
                  </span>

                  <h3>
                    Model scorecard
                  </h3>

                </div>


                <span className="verified-badge">
                  ✓ VALIDATED
                </span>

              </div>


              <div className="performance-values">

                <div>

                  <span>
                    ACCURACY
                  </span>

                  <strong>
                    70.27%
                  </strong>

                </div>


                <div>

                  <span>
                    F1 SCORE
                  </span>

                  <strong>
                    68.90%
                  </strong>

                </div>


                <div>

                  <span>
                    ROC-AUC
                  </span>

                  <strong>
                    76.24%
                  </strong>

                </div>

              </div>


              <div className="why-model">

                <strong>
                  Selected model
                </strong>

                <p>
                  XGBoost achieved the
                  strongest F1 score among the
                  trained models, with ROC-AUC
                  used as a supporting criterion.
                </p>

              </div>

            </div>


            <div className="features-card interactive-card">

              <div className="analytics-card-header">

                <div>

                  <span className="section-label">
                    FEATURE IMPORTANCE
                  </span>

                  <h3>
                    Strongest signals
                  </h3>

                  <p>
                    Most influential features in
                    the selected XGBoost model.
                  </p>

                </div>

              </div>


              <div className="feature-list">

                {topFeatures.length > 0 ? (

                  topFeatures.map(
                    (item, index) => {

                      const width =
                        (
                          item.importance /
                          maxImportance
                        ) * 100;


                      return (

                        <div
                          className="feature-row"
                          key={`${item.name}-${index}`}
                        >

                          <div className="feature-name">

                            <span>
                              {String(
                                index + 1
                              ).padStart(
                                2,
                                "0"
                              )}
                            </span>


                            <strong
                              title={
                                item.name
                              }
                            >
                              {item.name}
                            </strong>

                          </div>


                          <div className="feature-track">

                            <div
                              className="feature-bar-fill"
                              style={{
                                width:
                                  `${Math.max(
                                    width,
                                    3
                                  )}%`,
                              }}
                            ></div>

                          </div>


                          <span className="feature-value">

                            {item.importance.toFixed(
                              3
                            )}

                          </span>

                        </div>

                      );

                    }
                  )

                ) : (

                  <div className="empty-state">
                    Feature importance unavailable.
                  </div>

                )}

              </div>

            </div>

          </div>


          <div className="leakage-note">

            <span>
              i
            </span>

            <p>
              Post-delivery outcome fields were
              excluded from the prediction pipeline.
              The model uses features available before
              delivery to reduce target leakage.
            </p>

          </div>

        </section>


        {/* ==================================================
            CLOSING
            ================================================== */}

        <section className="closing-section interactive-card">

          <div className="closing-orb"></div>


          <div className="closing-content">

            <span className="section-label">
              LOGISTICS, BEFORE THE PROBLEM
            </span>


            <h2>

              Turn delivery risk

              <br />

              into an early signal.

            </h2>


            <p>

              Predict earlier. Prioritize smarter.
              Respond before delays become disruption.

            </p>


            <button
              type="button"
              className="primary-button"
              onClick={() =>
                navigateTo("prediction")
              }
            >

              Analyze a shipment

              <span>
                →
              </span>

            </button>

          </div>

        </section>


        {/* ==================================================
            FOOTER
            ================================================== */}

        <footer className="footer">

          <div className="footer-brand">

            <span className="brand-mark">
              L
            </span>

            <span>

              LogiSense
              <b>-AI</b>

            </span>

          </div>


          <span>
            ML · FastAPI · React
          </span>


          <span>
            Global Supply Chain Intelligence
          </span>

        </footer>

      </main>

    </div>
  );
}


export default App;