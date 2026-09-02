import React, { useState, useRef } from 'react';
import { useApp } from '../../context/AppContext';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { VitalCard } from '../../components/ui/VitalCard';
import { mockRecoveryGraphData } from '../../data/mockData';
import {
  Activity,
  Camera,
  Video,
  Upload,
  CheckCircle2,
  Clock,
  Pill,
  ArrowUpRight,
  ShieldCheck,
  Calendar,
  AlertTriangle,
  FileVideo,
  Sparkles,
  Check,
  X,
  RotateCcw,
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

export const PatientDashboard: React.FC = () => {
  const { currentPatient, medications, toggleMedicationStatus, setActiveTab } = useApp();

  // Video Monitoring State
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [videoPreviewUrl, setVideoPreviewUrl] = useState<string | null>(null);
  const [videoName, setVideoName] = useState<string>('');
  const [videoDuration, setVideoDuration] = useState<string>('00:48');
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [hasAnalysisResult, setHasAnalysisResult] = useState<boolean>(false);
  const [detectFallInVideo, setDetectFallInVideo] = useState<boolean>(false);
  const [fallAcknowledged, setFallAcknowledged] = useState<boolean>(false);
  const [showRecentAnalysisModal, setShowRecentAnalysisModal] = useState<boolean>(false);

  // File Picker Handler
  const handleVideoSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setVideoName(file.name);
      const url = URL.createObjectURL(file);
      setVideoPreviewUrl(url);
      setVideoDuration('00:48');
      setHasAnalysisResult(false);
      setFallAcknowledged(false);
    }
  };

  // Trigger Demo Analysis
  const handleAnalyzeVideo = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
      setHasAnalysisResult(true);
    }, 1200);
  };

  // Reset Video Upload
  const handleResetVideo = () => {
    setVideoPreviewUrl(null);
    setVideoName('');
    setHasAnalysisResult(false);
    setDetectFallInVideo(false);
    setFallAcknowledged(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* HEADER GREETING & STATUS BANNER */}
      <div className="bg-gradient-to-r from-teal-700 via-teal-800 to-slate-900 rounded-3xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden">
        <div className="absolute right-0 top-0 translate-x-8 -translate-y-8 w-64 h-64 bg-teal-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div>
            <div className="flex items-center gap-2 text-teal-300 text-xs font-bold uppercase tracking-wider mb-1">
              <Calendar className="w-4 h-4" />
              <span>{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' })}</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-black tracking-tight">
              Good Morning, {currentPatient.name.split(' ')[0]} 👋
            </h1>
            <p className="text-teal-100 text-sm mt-1">
              Surgery: <strong className="text-white">{currentPatient.surgeryType}</strong> • Post-Op Day {currentPatient.recoveryDay} of {currentPatient.targetRecoveryDays}
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-md p-4 rounded-2xl border border-white/20 flex items-center gap-4 shrink-0">
            <div>
              <span className="text-[11px] text-teal-200 uppercase font-bold tracking-wider block">Current Recovery Triage</span>
              <div className="mt-1">
                <StatusBadge status={currentPatient.status} size="lg" />
              </div>
            </div>
            <button
              onClick={() => setActiveTab('checkup')}
              className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold rounded-xl text-xs transition-all shadow-md active:scale-95 cursor-pointer"
            >
              Start Daily Checkup
            </button>
          </div>
        </div>
      </div>

      {/* HEALTH CARDS GRID */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <Activity className="w-5 h-5 text-teal-600" />
            <span>Today's Vital Telemetry</span>
          </h2>
          <span className="text-xs text-slate-500 font-medium">Auto-synced {currentPatient.lastUpdate}</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <VitalCard
            title="Temperature"
            value={currentPatient.vitals.temperature}
            unit="°F"
            idealRange="97.8 – 99.1 °F"
            status={currentPatient.vitals.temperature > 100.5 ? 'critical' : currentPatient.vitals.temperature > 99.2 ? 'warning' : 'normal'}
            type="temp"
            onClick={() => setActiveTab('checkup')}
          />
          <VitalCard
            title="Blood Pressure"
            value={`${currentPatient.vitals.bpSystolic}/${currentPatient.vitals.bpDiastolic}`}
            unit="mmHg"
            idealRange="120/80 mmHg"
            status={currentPatient.vitals.bpSystolic > 140 ? 'critical' : currentPatient.vitals.bpSystolic > 130 ? 'warning' : 'normal'}
            type="bp"
            onClick={() => setActiveTab('checkup')}
          />
          <VitalCard
            title="Heart Rate"
            value={currentPatient.vitals.heartRate}
            unit="bpm"
            idealRange="60 – 100 bpm"
            status={currentPatient.vitals.heartRate > 100 ? 'warning' : 'normal'}
            type="hr"
            onClick={() => setActiveTab('checkup')}
          />
          <VitalCard
            title="Oxygen Saturation (SpO2)"
            value={currentPatient.vitals.spO2}
            unit="%"
            idealRange="95 – 100 %"
            status={currentPatient.vitals.spO2 < 94 ? 'critical' : currentPatient.vitals.spO2 < 96 ? 'warning' : 'normal'}
            type="spo2"
            onClick={() => setActiveTab('checkup')}
          />
          <VitalCard
            title="Pain Level"
            value={`${currentPatient.vitals.painLevel}/10`}
            unit="Score"
            idealRange="0 – 3 / 10"
            status={currentPatient.vitals.painLevel > 6 ? 'critical' : currentPatient.vitals.painLevel > 4 ? 'warning' : 'normal'}
            type="pain"
            onClick={() => setActiveTab('checkup')}
          />
          <VitalCard
            title="Mobility Status"
            value={currentPatient.vitals.mobility.split(' ')[0]}
            unit={currentPatient.vitals.mobility}
            idealRange="Progressive rehab"
            status="normal"
            type="mobility"
            onClick={() => setActiveTab('checkup')}
          />
        </div>
      </div>

      {/* ========================================================================= */}
      {/* CAMERA + VIDEO MONITORING DUAL OPTIONS (SIDE-BY-SIDE ON DESKTOP, STACKED MOBILE) */}
      {/* ========================================================================= */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <Camera className="w-5 h-5 text-teal-600" />
            <span>Activity Monitoring Options</span>
          </h2>
          <span className="text-xs text-slate-500 font-medium">Real-time edge & recorded video analysis</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* OPTION 1: 📷 CAMERA MONITORING CARD */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs flex flex-col justify-between space-y-4 hover:shadow-md transition-shadow">
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2.5">
                  <div className="p-2.5 bg-emerald-50 text-emerald-600 rounded-2xl border border-emerald-100">
                    <Camera className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-extrabold text-slate-900 text-base flex items-center gap-1.5">
                      <span>📷 Camera Monitoring</span>
                    </h3>
                    <p className="text-xs text-slate-500">Live AI Activity Detection</p>
                  </div>
                </div>

                <span className="px-2.5 py-1 bg-emerald-100 text-emerald-800 text-xs font-bold rounded-full flex items-center gap-1.5 border border-emerald-200">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                  🟢 Connected
                </span>
              </div>

              {/* Status details */}
              <div className="bg-slate-50 rounded-2xl p-4 border border-slate-200/80 space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-slate-500 font-medium">Status:</span>
                  <span className="font-extrabold text-emerald-700">🟢 Connected</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500 font-medium">AI Activity Detection:</span>
                  <span className="font-bold text-teal-700 bg-teal-50 px-2 py-0.5 rounded-md border border-teal-100">
                    Active
                  </span>
                </div>
                <div className="flex items-center justify-between pt-1 border-t border-slate-200/60">
                  <span className="text-slate-500 font-medium">Latest activity:</span>
                  <strong className="text-slate-900 font-bold">Walking detected</strong>
                </div>
              </div>

              <div className="p-3 bg-teal-50/70 border border-teal-200/80 rounded-2xl text-[11px] text-teal-900 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-teal-600 shrink-0" />
                <span>Zero raw video stored. Anonymized posture metadata only.</span>
              </div>
            </div>

            <button
              onClick={() => setActiveTab('camera')}
              className="w-full py-3 bg-teal-600 hover:bg-teal-700 text-white font-extrabold rounded-2xl text-xs transition-all shadow-xs flex items-center justify-center gap-2 cursor-pointer active:scale-98"
            >
              <Camera className="w-4 h-4" />
              <span>Open Camera</span>
            </button>
          </div>

          {/* OPTION 2: 🎥 VIDEO MONITORING CARD */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs flex flex-col justify-between space-y-4 hover:shadow-md transition-shadow">
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2.5">
                  <div className="p-2.5 bg-blue-50 text-blue-600 rounded-2xl border border-blue-100">
                    <Video className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-extrabold text-slate-900 text-base flex items-center gap-1.5">
                      <span>🎥 Video Monitoring</span>
                    </h3>
                    <p className="text-xs text-slate-500">Recorded Post-Op Video Analytics</p>
                  </div>
                </div>

                <span className="px-2.5 py-1 bg-blue-100 text-blue-800 text-xs font-bold rounded-full border border-blue-200">
                  AI Video Intake
                </span>
              </div>

              <p className="text-xs text-slate-600 leading-relaxed">
                Upload a short recovery video for AI activity analysis.
              </p>

              {/* Hidden File Input */}
              <input
                type="file"
                ref={fileInputRef}
                accept=".mp4,.mov,.webm,.avi"
                onChange={handleVideoSelect}
                className="hidden"
              />

              {/* Video Select / Preview Area */}
              {videoPreviewUrl ? (
                <div className="bg-slate-900 rounded-2xl p-4 text-white space-y-3">
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2 font-bold truncate max-w-[200px]">
                      <FileVideo className="w-4 h-4 text-teal-400 shrink-0" />
                      <span className="truncate">{videoName}</span>
                    </div>
                    <button
                      onClick={handleResetVideo}
                      className="p-1 hover:bg-white/10 rounded-lg text-slate-400 hover:text-white"
                      title="Clear video"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Video Player Preview */}
                  <div className="relative rounded-xl overflow-hidden bg-slate-950 aspect-video flex items-center justify-center border border-slate-800">
                    <video
                      src={videoPreviewUrl}
                      controls
                      className="w-full h-full object-cover"
                      onLoadedMetadata={(e) => {
                        const d = Math.round(e.currentTarget.duration);
                        const mins = String(Math.floor(d / 60)).padStart(2, '0');
                        const secs = String(d % 60).padStart(2, '0');
                        setVideoDuration(`${mins}:${secs}`);
                      }}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-[11px] pt-1 border-t border-slate-800">
                    <div>
                      <span className="text-slate-400 block">Duration:</span>
                      <strong className="text-white font-bold">{videoDuration}</strong>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Upload Status:</span>
                      <strong className="text-emerald-400 font-bold">🟢 Uploaded & Ready</strong>
                    </div>
                  </div>
                </div>
              ) : (
                <div
                  onClick={() => fileInputRef.current?.click()}
                  className="border-2 border-dashed border-slate-200 hover:border-teal-400 rounded-2xl p-5 text-center cursor-pointer bg-slate-50/60 hover:bg-teal-50/40 transition-colors space-y-2"
                >
                  <div className="w-10 h-10 bg-teal-100 text-teal-700 rounded-xl mx-auto flex items-center justify-center">
                    <Upload className="w-5 h-5" />
                  </div>
                  <div className="text-xs font-bold text-slate-800">Click to Select Recovery Video</div>
                  <p className="text-[11px] text-slate-500">Supports .mp4, .mov, .webm, .avi</p>
                </div>
              )}
            </div>

            {/* Video Action Button */}
            {!videoPreviewUrl ? (
              <button
                onClick={() => fileInputRef.current?.click()}
                className="w-full py-3 bg-slate-900 hover:bg-slate-800 text-white font-extrabold rounded-2xl text-xs transition-all shadow-xs flex items-center justify-center gap-2 cursor-pointer active:scale-98"
              >
                <Upload className="w-4 h-4" />
                <span>Upload Video</span>
              </button>
            ) : (
              <div className="space-y-2">
                <button
                  onClick={handleAnalyzeVideo}
                  disabled={isAnalyzing}
                  className="w-full py-3 bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-700 hover:to-emerald-700 text-white font-extrabold rounded-2xl text-xs transition-all shadow-md flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                >
                  {isAnalyzing ? (
                    <>
                      <RotateCcw className="w-4 h-4 animate-spin" />
                      <span>Analyzing Recovery Postures...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      <span>Analyze Video</span>
                    </>
                  )}
                </button>
              </div>
            )}
          </div>

        </div>
      </div>

      {/* ========================================================================= */}
      {/* VIDEO ANALYSIS RESULT SECTION (SHOWS AFTER CLICKING ANALYZE VIDEO) */}
      {/* ========================================================================= */}
      {hasAnalysisResult && (
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6 animate-fadeIn">
          
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-teal-50 text-teal-600 rounded-2xl border border-teal-100">
                <Sparkles className="w-6 h-6" />
              </div>
              <div>
                <span className="text-[11px] uppercase font-extrabold tracking-wider text-teal-600">Post-Op Video Analysis</span>
                <h3 className="text-xl font-black text-slate-900">AI Activity Analysis</h3>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500 font-medium">Demo Simulator:</span>
              <button
                onClick={() => {
                  setDetectFallInVideo(!detectFallInVideo);
                  setFallAcknowledged(false);
                }}
                className={`px-3 py-1.5 rounded-xl text-xs font-extrabold border transition-colors cursor-pointer ${
                  detectFallInVideo
                    ? 'bg-rose-100 text-rose-800 border-rose-300'
                    : 'bg-slate-100 text-slate-700 border-slate-200 hover:bg-slate-200'
                }`}
              >
                {detectFallInVideo ? 'Fall Simulation: ON 🔴' : 'Simulate Fall Event ⚠️'}
              </button>
            </div>
          </div>

          {/* CRITICAL EVENT UI: PROMINENT RED CARD REQUIRED IF POSSIBLE FALL DETECTED */}
          {detectFallInVideo && !fallAcknowledged && (
            <div className="bg-gradient-to-r from-rose-600 via-red-600 to-rose-700 text-white rounded-3xl p-6 sm:p-7 shadow-2xl space-y-4 animate-pulse border-2 border-rose-200">
              <div className="flex items-center justify-between border-b border-white/20 pb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-white/20 rounded-xl">
                    <AlertTriangle className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <span className="text-[11px] font-black uppercase tracking-widest text-rose-200">URGENT CLINICAL ALERT</span>
                    <h4 className="text-2xl font-black text-white">🔴 POSSIBLE FALL DETECTED</h4>
                  </div>
                </div>
                <span className="px-3 py-1 bg-white text-rose-900 font-extrabold text-xs rounded-full">
                  HIGH SEVERITY
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs text-rose-100">
                <div>
                  <span className="text-rose-200 font-medium block">Confidence Score:</span>
                  <strong className="text-white text-base font-black">94%</strong>
                </div>
                <div>
                  <span className="text-rose-200 font-medium block">Time:</span>
                  <strong className="text-white text-base font-black">00:42</strong>
                </div>
                <div className="col-span-2 sm:col-span-1">
                  <span className="text-rose-200 font-medium block">Status:</span>
                  <strong className="text-amber-200 text-xs font-extrabold">Critical event detected</strong>
                </div>
              </div>

              <div className="flex items-center gap-3 pt-2">
                <button
                  onClick={() => setFallAcknowledged(true)}
                  className="px-5 py-2.5 bg-white text-rose-900 hover:bg-slate-100 font-extrabold text-xs rounded-xl transition-all shadow-md flex items-center gap-1.5 cursor-pointer"
                >
                  <Check className="w-4 h-4 text-emerald-600" />
                  <span>Acknowledge</span>
                </button>

                <button
                  onClick={() => setActiveTab('alerts')}
                  className="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-extrabold text-xs rounded-xl transition-all shadow-md flex items-center gap-1.5 cursor-pointer"
                >
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  <span>View Alert</span>
                </button>
              </div>
            </div>
          )}

          {/* AI ACTIVITY CONFIDENCE METRICS */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 text-center space-y-1">
              <span className="text-xs font-bold text-slate-700 block">🟢 Walking detected</span>
              <div className="text-lg font-black text-slate-900">96%</div>
              <span className="text-[10px] text-slate-400 font-medium">Confidence Score</span>
            </div>

            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 text-center space-y-1">
              <span className="text-xs font-bold text-slate-700 block">🪑 Sitting detected</span>
              <div className="text-lg font-black text-slate-900">94%</div>
              <span className="text-[10px] text-slate-400 font-medium">Confidence Score</span>
            </div>

            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 text-center space-y-1">
              <span className="text-xs font-bold text-slate-700 block">🧍 Standing detected</span>
              <div className="text-lg font-black text-slate-900">91%</div>
              <span className="text-[10px] text-slate-400 font-medium">Confidence Score</span>
            </div>

            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 text-center space-y-1">
              <span className="text-xs font-bold text-slate-700 block">🛏️ Bed Exit detected</span>
              <div className="text-lg font-black text-slate-900">89%</div>
              <span className="text-[10px] text-slate-400 font-medium">Confidence Score</span>
            </div>
          </div>

          {/* Possible Fall Status Indicator */}
          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 flex items-center justify-between text-xs">
            <span className="font-bold text-slate-700">Possible Fall:</span>
            {detectFallInVideo ? (
              <span className="px-3 py-1 bg-rose-100 text-rose-800 rounded-full font-black border border-rose-200">
                🔴 Detected at 00:42 (Confidence: 94%)
              </span>
            ) : (
              <span className="px-3 py-1 bg-emerald-100 text-emerald-800 rounded-full font-bold border border-emerald-200">
                🟢 Not detected
              </span>
            )}
          </div>

          {/* ACTIVITY TIMELINE REQUIRED BY SPEC */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">Video Event Timeline</h4>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 bg-white border border-slate-200 rounded-xl shadow-2xs">
                <span className="font-black text-teal-700 block">00:05</span>
                <span className="text-slate-800 font-semibold">🧍 Standing</span>
              </div>
              <div className="p-3 bg-white border border-slate-200 rounded-xl shadow-2xs">
                <span className="font-black text-teal-700 block">00:12</span>
                <span className="text-slate-800 font-semibold">🟢 Walking</span>
              </div>
              <div className="p-3 bg-white border border-slate-200 rounded-xl shadow-2xs">
                <span className="font-black text-teal-700 block">00:28</span>
                <span className="text-slate-800 font-semibold">🪑 Sitting</span>
              </div>
              <div className="p-3 bg-white border border-slate-200 rounded-xl shadow-2xs">
                <span className="font-black text-teal-700 block">00:45</span>
                <span className="text-slate-800 font-semibold">🛏️ Bed Exit</span>
              </div>
            </div>
          </div>

          {/* PRIVACY MANDATE NOTE REQUIRED BY SPEC */}
          <div className="p-4 bg-teal-50 border border-teal-200 rounded-2xl text-xs text-teal-900 space-y-1">
            <div className="flex items-center gap-2 font-bold">
              <ShieldCheck className="w-4 h-4 text-teal-600" />
              <span>Privacy & Medical Compliance Directive</span>
            </div>
            <p className="text-[11px] text-teal-800 leading-relaxed">
              Videos are analyzed for relevant recovery activities. Continuous surveillance and unnecessary video storage should be avoided.
            </p>
            <p className="text-[10px] text-teal-700 font-medium">
              • No facial recognition • No identity tracking by face • No continuous CCTV recording.
            </p>
          </div>

        </div>
      )}

      {/* ========================================================================= */}
      {/* RECENT VIDEO ANALYSIS WIDGET REQUIRED BY SPEC */}
      {/* ========================================================================= */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-start sm:items-center gap-4">
          <div className="p-3.5 bg-indigo-50 text-indigo-600 rounded-2xl border border-indigo-100 shrink-0">
            <FileVideo className="w-6 h-6" />
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <h3 className="font-extrabold text-slate-900 text-base">Recent Video Analysis</h3>
              <span className="px-2.5 py-0.5 bg-emerald-100 text-emerald-800 text-[10px] font-bold rounded-full border border-emerald-200">
                🟢 Normal Activity
              </span>
            </div>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-600">
              <span>Last analyzed: <strong className="text-slate-900 font-semibold">Recovery_Day_04.mp4</strong></span>
              <span>Result: <strong className="text-emerald-700 font-semibold">🟢 Normal Activity</strong></span>
              <span>Analyzed: <strong className="text-slate-700">Today, 10:42 AM</strong></span>
            </div>
          </div>
        </div>

        <button
          onClick={() => setShowRecentAnalysisModal(true)}
          className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl text-xs transition-colors shrink-0 cursor-pointer shadow-xs"
        >
          View Analysis
        </button>
      </div>

      {/* RECENT ANALYSIS POPUP MODAL */}
      {showRecentAnalysisModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 animate-fadeIn">
          <div className="bg-white w-full max-w-lg rounded-3xl p-6 sm:p-8 shadow-2xl border border-slate-200 space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <FileVideo className="w-5 h-5 text-indigo-600" />
                <h3 className="font-black text-slate-900 text-lg">Archived Video Analysis</h3>
              </div>
              <button
                onClick={() => setShowRecentAnalysisModal(false)}
                className="p-1 text-slate-400 hover:text-slate-600 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200 text-xs space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-500 font-medium">Video File:</span>
                <strong className="text-slate-900">Recovery_Day_04.mp4</strong>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-medium">Analyzed At:</span>
                <span className="text-slate-700">Today, 10:42 AM</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-medium">Overall Status:</span>
                <span className="text-emerald-700 font-bold">🟢 Normal Activity Verified</span>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-700 uppercase">Detection Summary</span>
                <span className="px-2 py-0.5 bg-slate-200 text-slate-700 text-[10px] font-bold rounded-md">source: mock demo</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2.5 bg-slate-100 rounded-xl">🟢 Walking: 96%</div>
                <div className="p-2.5 bg-slate-100 rounded-xl">🪑 Sitting: 94%</div>
                <div className="p-2.5 bg-slate-100 rounded-xl">🧍 Standing: 91%</div>
                <div className="p-2.5 bg-slate-100 rounded-xl">🛏️ Bed Exit: 89%</div>
              </div>
            </div>

            <div className="p-3 bg-teal-50 border border-teal-200 rounded-xl text-[11px] text-teal-800">
              For real YOLO Pose video analysis with live 17-keypoint fall detection, open the <strong>Camera Monitoring & Video Analysis</strong> tab.
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => {
                  setShowRecentAnalysisModal(false);
                  setActiveTab('camera');
                }}
                className="flex-1 py-2.5 bg-teal-600 hover:bg-teal-500 text-white font-bold rounded-xl text-xs transition-colors"
              >
                Open Real Video AI Mode
              </button>
              <button
                onClick={() => setShowRecentAnalysisModal(false)}
                className="px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl text-xs transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* TODAY'S MEDICATION SCHEDULE */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-teal-50 text-teal-600 rounded-xl">
              <Pill className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-base">Today's Medication Schedule</h3>
              <p className="text-xs text-slate-500">Prescribed by {currentPatient.doctorName}</p>
            </div>
          </div>

          <button
            onClick={() => setActiveTab('medications')}
            className="text-xs font-bold text-teal-600 hover:text-teal-700 flex items-center gap-1"
          >
            <span>Full Schedule</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {medications.slice(0, 3).map((med) => (
            <div
              key={med.id}
              className={`p-4 rounded-2xl border transition-all flex flex-col justify-between space-y-3 ${
                med.status === 'taken'
                  ? 'bg-emerald-50/50 border-emerald-200'
                  : med.status === 'missed'
                  ? 'bg-rose-50/50 border-rose-200'
                  : 'bg-slate-50 border-slate-200 hover:border-slate-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-slate-500" />
                  <span className="text-xs font-extrabold text-slate-900">{med.scheduledTime}</span>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded-md bg-white border border-slate-200 font-semibold text-slate-600">
                  {med.timing}
                </span>
              </div>

              <div>
                <h4 className="font-bold text-slate-900 text-sm">{med.name} ({med.dosage})</h4>
                <p className="text-[11px] text-slate-500 mt-0.5 line-clamp-2">{med.instructions}</p>
              </div>

              <div className="pt-2 border-t border-slate-200/60 flex items-center justify-between">
                {med.status === 'taken' ? (
                  <span className="px-3 py-1 bg-emerald-100 text-emerald-800 text-xs font-extrabold rounded-xl flex items-center gap-1 border border-emerald-300">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Taken
                  </span>
                ) : (
                  <button
                    onClick={() => toggleMedicationStatus(med.id, 'taken')}
                    className="w-full py-1.5 bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold rounded-xl shadow-xs transition-colors cursor-pointer"
                  >
                    Mark Taken
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="pt-2 border-t border-slate-100 text-xs text-slate-500 flex items-center justify-between">
          <span>Daily Adherence Target: <strong>100%</strong></span>
          <span className="font-bold text-emerald-600">87% Current Adherence</span>
        </div>
      </div>

      {/* RECOVERY PROGRESS CHART */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6">
          <div>
            <h3 className="font-bold text-slate-900 text-lg">Post-Operative Recovery Telemetry Chart</h3>
            <p className="text-xs text-slate-500">Tracking daily pain reduction, mobility score, and body temperature</p>
          </div>
          <div className="flex items-center gap-4 text-xs font-semibold">
            <span className="flex items-center gap-1.5 text-rose-600">
              <span className="w-3 h-3 rounded-full bg-rose-500" /> Pain Score (0-10)
            </span>
            <span className="flex items-center gap-1.5 text-teal-600">
              <span className="w-3 h-3 rounded-full bg-teal-500" /> Mobility Index %
            </span>
            <span className="flex items-center gap-1.5 text-amber-600">
              <span className="w-3 h-3 rounded-full bg-amber-500" /> Temperature (°F)
            </span>
          </div>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={mockRecoveryGraphData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="day" stroke="#64748b" fontSize={12} tickLine={false} />
              <YAxis stroke="#64748b" fontSize={12} tickLine={false} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderRadius: '12px', border: 'none', color: '#fff' }}
              />
              <Line type="monotone" dataKey="pain" name="Pain Level" stroke="#f43f5e" strokeWidth={3} dot={{ r: 4 }} />
              <Line type="monotone" dataKey="mobility" name="Mobility Index %" stroke="#14b8a6" strokeWidth={3} dot={{ r: 4 }} />
              <Line type="monotone" dataKey="temp" name="Temperature °F" stroke="#f59e0b" strokeWidth={2} strokeDasharray="5 5" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
};
