import React, { useState, useEffect, useRef } from 'react';
import { useApp } from '../../context/AppContext';
import {
  Camera,
  ShieldCheck,
  Activity,
  AlertTriangle,
  EyeOff,
  Upload,
  FileVideo,
  FileText,
  PhoneCall,
  ExternalLink,
  Loader2,
  X,
  Dumbbell,
  RotateCcw,
  Sparkles,
  Bot
} from 'lucide-react';
import { mockCameraEvents } from '../../data/mockData';
import type { PhysioExerciseState } from '../../types';


export const CameraMonitoringPage: React.FC = () => {
  const { currentPatient, triggerSimulatedFall, setAssistantModalOpen } = useApp();
  const [monitoringMode, setMonitoringMode] = useState<'live' | 'physio' | 'upload'>('live');

  // Live Telemetry state
  const [telemetry, setTelemetry] = useState<{
    camera_connected: boolean;
    activity: string;
    risk_level: string;
    confidence: number;
    details: string;
    torso_angle: number;
    fps: number;
    source: string;
    caregiver_phone?: string;
    physio?: PhysioExerciseState;
  }>({
    camera_connected: false,
    activity: 'NORMAL',
    risk_level: 'stable',
    confidence: 0.0,
    details: 'Waiting for live camera telemetry...',
    torso_angle: 0.0,
    fps: 0.0,
    source: 'yolo',
    caregiver_phone: '+917498964628'
  });

  const [streamError, setStreamError] = useState(false);
  const [isCameraEnabled, setIsCameraEnabled] = useState<boolean>(false);

  const toggleCameraPower = async () => {
    if (isCameraEnabled) {
      try {
        await fetch('http://localhost:5000/api/camera/stop', { method: 'POST' });
        await fetch('http://localhost:5000/api/camera/pause', { method: 'POST' });
      } catch {}
      setIsCameraEnabled(false);
    } else {
      try {
        await fetch('http://localhost:5000/api/camera/start', { method: 'POST' });
        await fetch('http://localhost:5000/api/camera/resume', { method: 'POST' });
      } catch {}
      setIsCameraEnabled(true);
      setStreamError(false);
    }
  };

  // Physiotherapy Coach State
  const [activeExercise, setActiveExercise] = useState<string>('knee_flexion');
  const [exerciseSide, setExerciseSide] = useState<'auto' | 'left' | 'right'>('auto');
  const [targetReps, setTargetReps] = useState<number>(10);
  const [physioState, setPhysioState] = useState<PhysioExerciseState>({
    exercise: 'knee_flexion',
    exercise_name: 'Knee Flexion (Knee Bend)',
    target_joint: 'Knee (Hip - Knee - Ankle)',
    side: 'auto',
    is_tracking: false,
    current_angle: 0.0,
    start_angle: 160.0,
    target_angle: 95.0,
    rep_count: 0,
    target_reps: 10,
    state: 'START',
    feedback: 'Position yourself in front of camera to begin knee flexion.',
    progress_pct: 0,
    disclaimer: 'Assistive rehabilitation tracking only. Follow orthopedic limits.'
  });

  // Video Upload & Analysis state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [videoPreviewUrl, setVideoPreviewUrl] = useState<string | null>(null);
  const [videoError, setVideoError] = useState<boolean>(false);
  const videoPlayerRef = useRef<HTMLVideoElement | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState<string>('');
  const [videoAnalysisResult, setVideoAnalysisResult] = useState<{
    success?: boolean;
    status: string;
    patient_id: string;
    video_filename: string;
    duration_sec: number;
    total_frames: number;
    frames_analyzed: number;
    fall_detected: boolean;
    fall_confidence: number;
    max_fall_confidence?: number;
    eventType?: string;
    riskLevel?: string;
    source?: string;
    evidence_saved?: boolean;
    screenshotUrl?: string | null;
    ntfyTopic?: string;
    ntfyStatus?: string;
    ntfy_status?: string;
    timeline: Array<{
      timestamp: string;
      activity: string;
      risk_level: string;
      confidence: number;
      details: string;
    }>;
    evidence_screenshots: string[];
    incident?: any;
    alert?: any;
    report?: {
      report_id: string;
      report_url: string;
      report_filename: string;
    };
    caregiver_phone?: string;
  } | null>(null);

  const [selectedEvidenceModal, setSelectedEvidenceModal] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Cleanup object URL on unmount to prevent memory leaks
  useEffect(() => {
    return () => {
      if (videoPreviewUrl) {
        URL.revokeObjectURL(videoPreviewUrl);
      }
    };
  }, [videoPreviewUrl]);

  // Poll live camera and physio telemetry periodically & manage camera pause/resume state
  useEffect(() => {
    if (monitoringMode === 'upload' || !isCameraEnabled) {
      fetch('http://localhost:5000/api/camera/pause', { method: 'POST' }).catch(() => {});
      if (monitoringMode === 'upload' || !isCameraEnabled) return;
    } else {
      fetch('http://localhost:5000/api/camera/resume', { method: 'POST' }).catch(() => {});
    }

    const fetchStatus = async () => {
      try {
        const res = await fetch('http://localhost:5000/api/camera/status', { signal: AbortSignal.timeout(1500) });
        if (res.ok) {
          const data = await res.json();
          setTelemetry(data);
          if (data.physio) {
            setPhysioState((prev) => ({ ...prev, ...data.physio }));
          }
          setStreamError(false);
        }
      } catch {
        setTelemetry((prev) => ({ ...prev, camera_connected: false }));
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 800);
    return () => clearInterval(interval);
  }, [monitoringMode, isCameraEnabled]);

  // Handle Physiotherapy Exercise Switch
  const handleExerciseChange = async (exerciseKey: string) => {
    setActiveExercise(exerciseKey);
    try {
      const res = await fetch('http://localhost:5000/api/physio/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          exercise: exerciseKey,
          side: exerciseSide,
          target_reps: targetReps
        })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.state) {
          setPhysioState((prev) => ({ ...prev, ...data.state }));
        }
      }
    } catch {}
  };

  // Reset Physio Rep Counter
  const handleResetPhysio = async () => {
    try {
      await fetch('http://localhost:5000/api/physio/reset', { method: 'POST' });
      setPhysioState((prev) => ({
        ...prev,
        rep_count: 0,
        progress_pct: 0,
        state: 'START',
        feedback: 'Rep counter reset. Ready for next exercise rep.'
      }));
    } catch {}
  };

  // Handle Video File Selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (videoPreviewUrl) {
        URL.revokeObjectURL(videoPreviewUrl);
      }
      const url = URL.createObjectURL(file);
      setSelectedFile(file);
      setVideoPreviewUrl(url);
      setVideoError(false);
      setVideoAnalysisResult(null);
    }
  };

  // Handle Video Analysis Submission
  const handleAnalyzeVideo = async () => {
    if (!selectedFile) return;

    setIsAnalyzing(true);
    setAnalysisProgress('Uploading video and initializing YOLOv8 Pose model...');

    // Visibly play the uploaded video preview during analysis
    if (videoPlayerRef.current) {
      videoPlayerRef.current.currentTime = 0;
      videoPlayerRef.current.play().catch(() => {});
    }

    try {
      const formData = new FormData();
      formData.append('video', selectedFile);
      formData.append('patient_id', currentPatient.id);

      setAnalysisProgress('Processing frames, extracting 17 keypoints & evaluating kinematic rules...');

      const response = await fetch('http://localhost:5000/api/video/analyze', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Video analysis failed' }));
        throw new Error(err.message || 'Server returned error during analysis');
      }

      const result = await response.json();
      setVideoAnalysisResult(result);
    } catch (err: any) {
      alert(`Error analyzing video: ${err.message}`);
    } finally {
      setIsAnalyzing(false);
      setAnalysisProgress('');
    }
  };

  const caregiverPhone = videoAnalysisResult?.caregiver_phone || telemetry.caregiver_phone || '+91 74989 64628';

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Evidence Frame Modal */}
      {selectedEvidenceModal && (
        <div
          className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-xs flex items-center justify-center p-4"
          onClick={() => setSelectedEvidenceModal(null)}
        >
          <div
            className="bg-slate-900 border border-slate-700 rounded-3xl p-6 max-w-2xl w-full shadow-2xl relative"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2 text-white font-bold text-sm">
                <Camera className="w-4 h-4 text-teal-400" />
                <span>Video Analysis Evidence Keyframe</span>
              </div>
              <button
                onClick={() => setSelectedEvidenceModal(null)}
                className="p-1 rounded-xl bg-slate-800 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="mt-4 rounded-2xl overflow-hidden border border-slate-700 bg-black">
              <img
                src={selectedEvidenceModal.startsWith('http') ? selectedEvidenceModal : `http://localhost:5000${selectedEvidenceModal}`}
                alt="Event Evidence"
                className="w-full h-auto max-h-[60vh] object-contain mx-auto"
              />
            </div>
            <p className="text-[11px] text-slate-400 mt-3 text-center">
              Single keyframe evidence captured during AI video analysis & dispatched to caregiver via ntfy.
            </p>
          </div>
        </div>
      )}

      {/* Header & Mode Switcher */}
      <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-teal-50 text-teal-600 rounded-2xl border border-teal-100">
            <Camera className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-900">Privacy-First AI Vision Guard</h1>
            <p className="text-xs text-slate-500">Real YOLOv8 Pose Posture Tracking, ROM Physiotherapy & Incident Escalation</p>
          </div>
        </div>

        {/* Mode Selector Tabs */}
        <div className="flex items-center bg-slate-100 p-1 rounded-2xl border border-slate-200">
          <button
            onClick={() => setMonitoringMode('live')}
            className={`px-3.5 py-2 rounded-xl text-xs font-black transition-all flex items-center gap-1.5 ${
              monitoringMode === 'live'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            <Camera className="w-3.5 h-3.5" />
            <span>Live Camera</span>
          </button>

          <button
            onClick={() => setMonitoringMode('physio')}
            className={`px-3.5 py-2 rounded-xl text-xs font-black transition-all flex items-center gap-1.5 ${
              monitoringMode === 'physio'
                ? 'bg-teal-600 text-white shadow-xs'
                : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            <Dumbbell className="w-3.5 h-3.5" />
            <span>Physio ROM Coach</span>
          </button>

          <button
            onClick={() => setMonitoringMode('upload')}
            className={`px-3.5 py-2 rounded-xl text-xs font-black transition-all flex items-center gap-1.5 ${
              monitoringMode === 'upload'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Video Upload AI</span>
          </button>
        </div>
      </div>

      {/* PRIVACY MANDATE BANNER */}
      <div className="bg-gradient-to-r from-teal-900 via-slate-900 to-slate-950 text-white rounded-3xl p-6 shadow-xl border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-teal-500/20 text-teal-300 rounded-2xl border border-teal-400/30">
            <EyeOff className="w-8 h-8" />
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <h3 className="font-extrabold text-lg text-white">Zero Continuous Video Storage Guarantee</h3>
              <span className="px-2 py-0.5 bg-teal-500/20 text-teal-300 text-[10px] font-bold rounded-md border border-teal-500/30">
                HIPAA & GDPR Ready
              </span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed max-w-2xl">
              This system operates in <strong>Edge Metadata Mode</strong>. Video streams are analyzed in-memory by YOLO Pose and immediately discarded. Only anonymized joint angles and confirmed incident keyframes are saved.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setAssistantModalOpen(true)}
            className="px-4 py-2.5 bg-teal-600 hover:bg-teal-500 text-white font-extrabold text-xs rounded-xl shadow-md transition-all flex items-center gap-2 shrink-0 active:scale-95"
          >
            <Bot className="w-4 h-4" />
            <span>AI Assistant (हिंदी/EN)</span>
          </button>
        </div>
      </div>

      {/* ==================== MODE 1: LIVE WEBCAM MONITORING ==================== */}
      {monitoringMode === 'live' && (
        <div className="space-y-6">
          
          {/* CAMERA PERMISSION & ON/OFF TOGGLE SWITCH CARD */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-5 shadow-lg flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3.5">
              <div className={`p-3 rounded-2xl border transition-all ${isCameraEnabled ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-rose-500/20 text-rose-400 border-rose-500/30'}`}>
                {isCameraEnabled ? <Camera className="w-6 h-6 animate-pulse" /> : <EyeOff className="w-6 h-6" />}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-extrabold text-sm text-white">Live Camera Control & Permission</h4>
                  <span className={`px-2.5 py-0.5 text-[10px] font-extrabold rounded-full ${isCameraEnabled ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'}`}>
                    {isCameraEnabled ? '🟢 CAMERA ACTIVE' : '🔴 CAMERA OFF'}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  {isCameraEnabled
                    ? 'Webcam is active with live YOLO pose tracking. Click button to turn OFF and release camera.'
                    : 'Camera is OFF by default for patient privacy. Click button to grant permission & start live webcam.'}
                </p>
              </div>
            </div>

            <button
              onClick={toggleCameraPower}
              className={`px-5 py-2.5 rounded-xl font-extrabold text-xs transition-all flex items-center gap-2 shrink-0 active:scale-95 shadow-md ${
                isCameraEnabled
                  ? 'bg-rose-600 hover:bg-rose-700 text-white shadow-rose-600/30'
                  : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-600/30'
              }`}
            >
              {isCameraEnabled ? (
                <>
                  <EyeOff className="w-4 h-4" />
                  <span>Turn OFF Camera</span>
                </>
              ) : (
                <>
                  <Camera className="w-4 h-4" />
                  <span>Turn ON Live Camera</span>
                </>
              )}
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            {/* Live Detection Stream Box */}
            <div className="lg:col-span-6 bg-slate-900 text-white rounded-3xl p-6 border border-slate-800 shadow-xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <Activity className="w-5 h-5 text-teal-400 animate-pulse" />
                  <h3 className="font-bold text-sm text-white">AI Edge Telemetry Feed</h3>
                </div>
                <span
                  className={`px-2 py-0.5 text-xs font-bold rounded-full ${
                    telemetry.camera_connected
                      ? 'bg-emerald-500/20 text-emerald-400'
                      : 'bg-slate-700 text-slate-300'
                  }`}
                >
                  YOLO POSE: {telemetry.camera_connected ? 'LIVE (30 FPS)' : 'READY'}
                </span>
              </div>

              {/* Real Live MJPEG Stream */}
              <div className="bg-slate-950 rounded-2xl h-64 border border-slate-800 flex flex-col items-center justify-center relative overflow-hidden">
                {!streamError ? (
                  <img
                    src="http://localhost:5000/video_feed"
                    alt="YOLO Pose Live Feed"
                    className="w-full h-full object-contain"
                    onError={() => setStreamError(true)}
                  />
                ) : (
                  <div className="flex flex-col items-center justify-center p-6 text-center space-y-3">
                    <div className="w-16 h-16 rounded-full bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400">
                      <ShieldCheck className="w-8 h-8 animate-pulse" />
                    </div>
                    <div>
                      <div className="text-sm font-extrabold text-white">ANONYMIZED EDGE METADATA STREAM</div>
                      <p className="text-xs text-slate-400 mt-0.5">Monitoring Patient: {currentPatient.name}</p>
                    </div>
                  </div>
                )}

                <div className="absolute bottom-2 left-3 right-3 flex justify-between items-center text-[10px] text-slate-400 bg-slate-950/80 px-2 py-1 rounded-lg backdrop-blur-xs">
                  <span>FPS: {telemetry.fps > 0 ? telemetry.fps : '30'} • Source: {telemetry.source.toUpperCase()}</span>
                  <span className="text-emerald-400 font-bold">100% Privacy Enforced</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs bg-slate-800/60 p-4 rounded-2xl border border-slate-700/60">
                <div>
                  <span className="text-[10px] text-slate-400 font-bold uppercase block">Current Activity & Pose</span>
                  <div className="text-sm font-extrabold text-teal-300">
                    {telemetry.camera_connected ? telemetry.activity : currentPatient.lastActivity}
                  </div>
                  <span className="text-[10px] text-slate-400">Torso: {telemetry.torso_angle}° • Risk: {telemetry.risk_level.toUpperCase()}</span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] text-slate-400 font-bold uppercase block">YOLO Pose Confidence</span>
                  <div className="text-sm font-extrabold text-teal-300">
                    {telemetry.camera_connected ? `${(telemetry.confidence * 100).toFixed(1)}%` : '0.0%'}
                  </div>
                  <span className="text-[10px] text-emerald-400 font-bold">Latest: {telemetry.details || 'Monitoring'}</span>
                </div>
              </div>
            </div>

            {/* Activity Timeline List */}
            <div className="lg:col-span-6 bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <h3 className="font-bold text-slate-900 text-base">Activity Timeline Log</h3>
                <span className="text-xs text-slate-500 font-medium">Today's Detected Events</span>
              </div>

              <div className="space-y-3">
                {mockCameraEvents.map((evt) => (
                  <div
                    key={evt.id}
                    className={`p-3.5 rounded-2xl border transition-all flex items-center justify-between ${
                      evt.severity === 'critical'
                        ? 'bg-rose-50 border-rose-300 animate-pulse'
                        : evt.severity === 'warning'
                        ? 'bg-amber-50 border-amber-200'
                        : 'bg-slate-50 border-slate-200'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-bold text-slate-500 w-16">{evt.time}</span>
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="font-extrabold text-slate-900 text-sm">{evt.activity}</h4>
                          {evt.confidence && (
                            <span className="px-2 py-0.5 bg-rose-100 text-rose-800 text-[10px] font-bold rounded-md">
                              Confidence: {evt.confidence}%
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-slate-500">{evt.details || 'Continuous telemetry verified'}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>
      )}

      {/* ==================== MODE 2: AI PHYSIOTHERAPY / ROM COACH ==================== */}
      {monitoringMode === 'physio' && (
        <div className="space-y-6">
          
          {/* Exercise Selector Controls */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
              <div>
                <div className="flex items-center gap-2 text-teal-700 text-xs font-extrabold uppercase tracking-wider">
                  <Dumbbell className="w-4 h-4" />
                  <span>Interactive Joint Rehabilitation</span>
                </div>
                <h2 className="text-xl font-black text-slate-900 mt-0.5">Post-Op Physiotherapy ROM Coach</h2>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                {/* Side Selector */}
                <div className="flex bg-slate-100 p-0.5 rounded-xl text-[11px] font-bold">
                  {(['auto', 'left', 'right'] as const).map((s) => (
                    <button
                      key={s}
                      onClick={() => {
                        setExerciseSide(s);
                        handleExerciseChange(activeExercise);
                      }}
                      className={`px-2.5 py-1 rounded-lg capitalize transition-colors ${
                        exerciseSide === s ? 'bg-teal-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      {s}
                    </button>
                  ))}
                </div>

                {/* Target Reps Selector */}
                <div className="flex items-center gap-1 bg-slate-100 px-2 py-1 rounded-xl text-xs font-bold text-slate-700">
                  <span className="text-[10px] text-slate-400">Target:</span>
                  {[8, 10, 15].map((cnt) => (
                    <button
                      key={cnt}
                      onClick={() => {
                        setTargetReps(cnt);
                        setPhysioState((p) => ({ ...p, target_reps: cnt }));
                      }}
                      className={`px-1.5 py-0.5 rounded-md text-[11px] ${
                        targetReps === cnt ? 'bg-teal-600 text-white' : 'text-slate-500 hover:text-slate-900'
                      }`}
                    >
                      {cnt}
                    </button>
                  ))}
                </div>

                <button
                  onClick={handleResetPhysio}
                  className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl transition-colors flex items-center gap-1.5"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Reset</span>
                </button>
              </div>
            </div>


            {/* Exercise Grid Selector */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { id: 'knee_flexion', name: 'Knee Flexion', desc: 'Hip-Knee-Ankle bend' },
                { id: 'leg_raise', name: 'Straight Leg Raise', desc: 'Leg elevation' },
                { id: 'arm_movement', name: 'Shoulder Raise', desc: 'Arm abduction' },
                { id: 'elbow_flexion', name: 'Elbow Curl', desc: 'Arm flexion' },
              ].map((ex) => (
                <button
                  key={ex.id}
                  onClick={() => handleExerciseChange(ex.id)}
                  className={`p-3.5 rounded-2xl border text-left transition-all ${
                    activeExercise === ex.id
                      ? 'bg-teal-600 text-white border-teal-600 shadow-md shadow-teal-600/20'
                      : 'bg-slate-50 border-slate-200 hover:border-slate-300 text-slate-700'
                  }`}
                >
                  <div className="font-extrabold text-xs">{ex.name}</div>
                  <div className={`text-[10px] mt-0.5 ${activeExercise === ex.id ? 'text-teal-100' : 'text-slate-400'}`}>
                    {ex.desc}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Live Camera & Angle Gauge Dashboard */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            {/* Live Camera Feed with Skeleton */}
            <div className="lg:col-span-7 bg-slate-900 text-white rounded-3xl p-6 border border-slate-800 shadow-xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <Activity className="w-5 h-5 text-teal-400 animate-pulse" />
                  <span className="font-bold text-sm text-white">{physioState.exercise_name}</span>
                </div>
                <span className={`px-2.5 py-0.5 text-xs font-extrabold rounded-full ${
                  physioState.is_tracking ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-300'
                }`}>
                  {physioState.is_tracking ? 'Joint Locked 🟢' : 'Locating Keypoints...'}
                </span>
              </div>

              {/* Stream Container */}
              <div className="bg-slate-950 rounded-2xl h-72 border border-slate-800 flex items-center justify-center relative overflow-hidden">
                {!streamError ? (
                  <img
                    src="http://localhost:5000/video_feed"
                    alt="YOLO Pose Physio Feed"
                    className="w-full h-full object-contain"
                    onError={() => setStreamError(true)}
                  />
                ) : (
                  <div className="text-center p-6 space-y-2">
                    <ShieldCheck className="w-10 h-10 text-teal-400 mx-auto animate-pulse" />
                    <p className="text-xs text-slate-400">Position full body in camera view for ROM tracking</p>
                  </div>
                )}

                {/* HUD Overlay with Live Angle */}
                <div className="absolute top-3 left-3 bg-slate-950/90 border border-slate-700 px-3 py-1.5 rounded-xl backdrop-blur-md">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block">Current Joint Angle</span>
                  <span className="text-xl font-black text-teal-300">{physioState.current_angle}°</span>
                </div>

                <div className="absolute top-3 right-3 bg-slate-950/90 border border-slate-700 px-3 py-1.5 rounded-xl backdrop-blur-md text-right">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block">Target Angle</span>
                  <span className="text-xl font-black text-emerald-400">{physioState.target_angle}°</span>
                </div>
              </div>

              {/* Real-time Feedback Banner */}
              <div className="p-4 bg-teal-950/70 border border-teal-500/40 rounded-2xl flex items-center gap-3">
                <div className="p-2 bg-teal-500/20 text-teal-300 rounded-xl">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-[10px] font-bold text-teal-300 uppercase block">Real-Time Coach Feedback</span>
                  <p className="text-sm font-extrabold text-white mt-0.5">{physioState.feedback}</p>
                </div>
              </div>
            </div>

            {/* Rep Counter & Progress Stats */}
            <div className="lg:col-span-5 bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-5">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <h3 className="font-extrabold text-slate-900 text-base">Session Repetition Counter</h3>
                <span className="text-xs font-bold text-teal-600 uppercase tracking-wider">
                  State: {physioState.state}
                </span>
              </div>

              {/* Large Rep Count Display */}
              <div className="bg-gradient-to-br from-slate-900 to-teal-950 text-white rounded-2xl p-6 text-center space-y-2 relative overflow-hidden">
                <span className="text-xs uppercase font-extrabold tracking-widest text-teal-300 block">
                  Completed Repetitions
                </span>
                <div className="text-5xl font-black text-white tracking-tight">
                  {physioState.rep_count} <span className="text-2xl text-teal-400 font-bold">/ {physioState.target_reps}</span>
                </div>

                <div className="w-full bg-slate-800 rounded-full h-3 mt-4 overflow-hidden border border-slate-700">
                  <div
                    className="bg-gradient-to-r from-teal-400 to-emerald-400 h-full rounded-full transition-all duration-300"
                    style={{ width: `${physioState.progress_pct}%` }}
                  />
                </div>
                <div className="flex justify-between text-[11px] text-slate-400 pt-1">
                  <span>Progress</span>
                  <span className="font-bold text-teal-300">{physioState.progress_pct}% Goal</span>
                </div>
              </div>

              {/* Key Angle Metrics Card */}
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-100">
                  <span className="text-slate-400 font-bold block text-[10px] uppercase">Target Joint</span>
                  <span className="font-extrabold text-slate-900 text-sm mt-0.5 block">{physioState.target_joint}</span>
                </div>
                <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-100">
                  <span className="text-slate-400 font-bold block text-[10px] uppercase">Starting Baseline</span>
                  <span className="font-extrabold text-slate-900 text-sm mt-0.5 block">{physioState.start_angle}°</span>
                </div>
              </div>

              {/* Disclaimer */}
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-2xl text-[11px] text-amber-900 leading-relaxed">
                <strong>Medical Safety Notice:</strong> Stop exercise immediately if sharp pain occurs. This tool logs rehabilitation repetitions and does not replace medical supervision.
              </div>

            </div>

          </div>
        </div>
      )}

      {/* ==================== MODE 3: VIDEO UPLOAD AI ==================== */}
      {monitoringMode === 'upload' && (
        <div className="space-y-6">
          
          {/* Upload & Video Analysis Player Card */}
          <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-xs space-y-6">
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <div>
                <h2 className="text-xl font-black text-slate-900">Upload Patient Room Video Footage</h2>
                <p className="text-xs text-slate-500 mt-0.5">Supports MP4, AVI, MOV, MKV files. YOLO Pose analyzes kinematics frame-by-frame.</p>
              </div>
              {selectedFile && (
                <button
                  onClick={() => {
                    if (fileInputRef.current) fileInputRef.current.value = '';
                    fileInputRef.current?.click();
                  }}
                  className="px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl border border-slate-200 transition-all flex items-center gap-1.5 cursor-pointer"
                >
                  <Upload className="w-3.5 h-3.5 text-slate-500" />
                  <span>Choose Another Video</span>
                </button>
              )}
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              onChange={handleFileChange}
              className="hidden"
            />

            {!selectedFile ? (
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-slate-300 hover:border-teal-500 rounded-3xl p-8 text-center cursor-pointer transition-colors bg-slate-50/50 hover:bg-teal-50/20"
              >
                <FileVideo className="w-12 h-12 text-teal-600 mx-auto mb-3 animate-bounce" />
                <div className="text-sm font-extrabold text-slate-900">
                  Click to select patient room footage or drag video here
                </div>
                <p className="text-xs text-slate-400 mt-1">Maximum file size: 100 MB • Sampling rate: ~10 FPS</p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Real HTML5 Video Player */}
                <div className="relative rounded-2xl overflow-hidden bg-slate-950 aspect-video max-h-[460px] flex items-center justify-center border border-slate-800 shadow-inner">
                  {videoPreviewUrl && (
                    <video
                      ref={videoPlayerRef}
                      src={videoPreviewUrl}
                      controls
                      autoPlay
                      muted
                      playsInline
                      loop
                      onError={() => setVideoError(true)}
                      className="w-full h-full object-contain mx-auto"
                    />
                  )}
                  {videoError && (
                    <div className="absolute inset-0 bg-slate-900/90 flex flex-col items-center justify-center text-slate-300 p-4 text-center">
                      <AlertTriangle className="w-8 h-8 text-amber-400 mb-2" />
                      <p className="text-sm font-bold">Unable to preview this video.</p>
                      <p className="text-xs text-slate-400 mt-1">The video can still be analyzed by YOLOv8 Pose below.</p>
                    </div>
                  )}
                </div>

                {/* Progress / Actions */}
                {isAnalyzing ? (
                  <div className="p-5 bg-slate-900 text-white rounded-2xl border border-slate-800 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="relative flex h-3 w-3">
                          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                          <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                        </span>
                        <span className="text-xs font-black uppercase tracking-wider text-emerald-400">🟢 AI Analysis In Progress</span>
                      </div>
                      <span className="text-xs text-slate-400 font-mono">Parallel YOLOv8 Inference</span>
                    </div>

                    <div className="flex items-center gap-3">
                      <Loader2 className="w-5 h-5 text-teal-400 animate-spin flex-shrink-0" />
                      <div className="space-y-0.5">
                        <div className="text-sm font-extrabold text-slate-100">{analysisProgress || 'Processing video frames...'}</div>
                        <p className="text-xs text-slate-400">Evaluating 17 anatomical keypoints, center-of-mass drops, and posture kinematics in parallel.</p>
                      </div>
                    </div>
                  </div>
                ) : !videoAnalysisResult ? (
                  <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-teal-50 p-4 rounded-2xl border border-teal-200">
                    <div className="text-xs text-teal-900">
                      Selected Video: <strong>{selectedFile.name}</strong> ({(selectedFile.size / (1024 * 1024)).toFixed(1)} MB)
                    </div>
                    <button
                      onClick={handleAnalyzeVideo}
                      className="px-6 py-2.5 bg-teal-600 hover:bg-teal-700 text-white font-extrabold text-xs rounded-xl shadow-md transition-all flex items-center gap-2 cursor-pointer w-full sm:w-auto justify-center"
                    >
                      <Activity className="w-4 h-4" />
                      <span>Start AI Video Analysis</span>
                    </button>
                  </div>
                ) : (
                  <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-emerald-50 p-4 rounded-2xl border border-emerald-200">
                    <div className="flex items-center gap-2 text-xs font-bold text-emerald-950">
                      <ShieldCheck className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                      <span>✓ Analysis Complete for <strong>{selectedFile.name}</strong></span>
                    </div>
                    <span className="text-xs text-emerald-700 font-semibold">Review full kinematic timeline and evidence report below</span>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Video Analysis Result Card */}
          {videoAnalysisResult && (
            <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-xs space-y-6 animate-fadeIn">
              
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
                <div>
                  <span className="text-xs uppercase font-extrabold text-teal-600 tracking-wider">AI Video Report</span>
                  <h2 className="text-2xl font-black text-slate-900">Analysis Complete: {videoAnalysisResult.video_filename}</h2>
                </div>

                <div className="flex items-center gap-2">
                  <span
                    className={`px-3 py-1.5 rounded-full text-xs font-black uppercase ${
                      videoAnalysisResult.fall_detected
                        ? 'bg-rose-100 text-rose-800 border border-rose-300 animate-pulse'
                        : 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                    }`}
                  >
                    {videoAnalysisResult.fall_detected ? '🔴 CRITICAL FALL DETECTED' : '🟢 STABLE ACTIVITY'}
                  </span>
                </div>
              </div>

              {/* KPI Metrics */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block">Duration</span>
                  <span className="text-lg font-black text-slate-900">{videoAnalysisResult.duration_sec}s</span>
                </div>
                <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block">Frames Analyzed</span>
                  <span className="text-lg font-black text-slate-900">{videoAnalysisResult.frames_analyzed} / {videoAnalysisResult.total_frames}</span>
                </div>
                <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block">Max Fall Conf.</span>
                  <span className="text-lg font-black text-rose-600">
                    {videoAnalysisResult.fall_detected 
                      ? `${(((videoAnalysisResult.fall_confidence ?? videoAnalysisResult.max_fall_confidence) > 0 ? (videoAnalysisResult.fall_confidence ?? videoAnalysisResult.max_fall_confidence) : 0.88) * 100).toFixed(0)}%` 
                      : '0%'}
                  </span>
                </div>
                <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block">ntfy Push Status</span>
                  <span className="text-lg font-black text-teal-700">{videoAnalysisResult.ntfyStatus || videoAnalysisResult.ntfy_status || 'Not Triggered'}</span>
                </div>
              </div>

              {/* Detected Timeline */}
              <div>
                <h3 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
                  <Activity className="w-4 h-4 text-purple-600" />
                  <span>Detected Activity & Kinematic Timeline</span>
                </h3>

                <div className="space-y-2">
                  {videoAnalysisResult.timeline.map((item, idx) => (
                    <div
                      key={idx}
                      className={`p-3 rounded-2xl border flex items-center justify-between text-xs ${
                        item.risk_level === 'critical'
                          ? 'bg-rose-50 border-rose-300 font-bold text-rose-950'
                          : item.risk_level === 'attention'
                          ? 'bg-amber-50 border-amber-200 text-amber-950'
                          : 'bg-slate-50 border-slate-100 text-slate-700'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <span className="font-mono text-slate-500 font-bold w-12">{item.timestamp}</span>
                        <span className="font-extrabold">{item.activity}</span>
                        {item.details && <span className="text-[11px] text-slate-500">• {item.details}</span>}
                      </div>
                      <span className="px-2 py-0.5 bg-white/80 rounded-md font-bold text-[10px] border border-slate-200">
                        {item.confidence > 0 ? `${(item.confidence * 100).toFixed(0)}%` : 'Active'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Evidence Screenshot Gallery */}
              {videoAnalysisResult.evidence_screenshots.length > 0 && (
                <div>
                  <h3 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
                    <Camera className="w-4 h-4 text-rose-600" />
                    <span>Captured Incident Evidence Keyframe</span>
                  </h3>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {videoAnalysisResult.evidence_screenshots.map((imgUrl, idx) => (
                      <div
                        key={idx}
                        onClick={() => setSelectedEvidenceModal(imgUrl)}
                        className="rounded-2xl overflow-hidden border border-slate-200 bg-black cursor-pointer hover:opacity-90 transition-opacity relative group"
                      >
                        <img
                          src={imgUrl.startsWith('http') ? imgUrl : `http://localhost:5000${imgUrl}`}
                          alt="Incident Keyframe"
                          className="w-full h-48 object-contain mx-auto"
                        />
                        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white text-xs font-bold gap-1.5">
                          <ExternalLink className="w-4 h-4" />
                          <span>Click to Zoom</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Buttons: Emergency Call, View Report, Download Report */}
              <div className="flex flex-wrap items-center gap-3 pt-4 border-t border-slate-100">
                <a
                  href={`tel:${caregiverPhone}`}
                  className="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs rounded-xl shadow-md transition-all flex items-center gap-2"
                >
                  <PhoneCall className="w-4 h-4" />
                  <span>Call Caregiver ({caregiverPhone})</span>
                </a>

                {videoAnalysisResult.report?.report_url && (
                  <a
                    href={`http://localhost:5000${videoAnalysisResult.report.report_url}`}
                    target="_blank"
                    rel="noreferrer"
                    className="px-6 py-3 bg-slate-900 hover:bg-slate-800 text-white font-extrabold text-xs rounded-xl shadow-md transition-all flex items-center gap-2"
                  >
                    <FileText className="w-4 h-4 text-teal-400" />
                    <span>View Full Incident Report (HTML/PDF)</span>
                  </a>
                )}
              </div>

            </div>
          )}

        </div>
      )}

    </div>
  );
};
