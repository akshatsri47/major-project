"use client"
import { useEffect,useRef,useState,use } from "react"
export default function CallPage({params}:{params:Promise<{room:string}>}){
    const resolvedParams = use(params);
    const roomId = resolvedParams.room
    const [status,setstatus] = useState("idle")
    const [shareUrl, setShareUrl] = useState<string>("")
    const pcRef = useRef<RTCPeerConnection | null>(null);
    const audioRef = useRef<HTMLAudioElement | null>(null);
    
    useEffect(() => {
        if (typeof window !== "undefined") {
            setShareUrl(window.location.href);
        }
    }, []);
    
    async function startCall(){
        try {
            setstatus("requesting microphone")
            const stream = await navigator.mediaDevices.getUserMedia({audio:true})
            const pc = new RTCPeerConnection({
                iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
            });
            
            pcRef.current = pc;
            stream.getTracks().forEach((track) => pc.addTrack(track,stream));
            
            // Monitor connection state
            pc.onconnectionstatechange = () => {
                setstatus(`connection: ${pc.connectionState}`)
                if (pc.connectionState === "connected") {
                    setstatus("connected to partner")
                } else if (pc.connectionState === "failed") {
                    setstatus("connection failed")
                }
            }
            
            pc.ontrack = (event) => {
                setstatus("receiving audio from partner")
                if(audioRef.current){
                    audioRef.current.srcObject = event.streams[0];
                }
            }
            
            // Handle ICE candidates (for proper connection establishment)
            pc.oniceconnectionstatechange = () => {
                console.log("ICE connection state:", pc.iceConnectionState)
            }
            
            const offer = await pc.createOffer();
            await pc.setLocalDescription(offer);
            
            const res = await fetch("http://localhost:9000/offer", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  sdp: pc.localDescription?.sdp,
                  type: pc.localDescription?.type,
                  room: roomId,
                }),
            });
            
            if (!res.ok) {
                const error = await res.json()
                setstatus(`error: ${error.error || res.statusText}`)
                return
            }
            
            const answer = await res.json();
            await pc.setRemoteDescription(new RTCSessionDescription(answer));
            setstatus("waiting for partner")
        } catch (error) {
            console.error("Call error:", error)
            setstatus(`error: ${error instanceof Error ? error.message : "unknown error"}`)
        }
    }
    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-900 text-slate-100">
          <div className="bg-slate-950 p-6 rounded-xl shadow-xl w-80 text-center">
            <h2 className="text-xl mb-4">🎧 1-to-1 Audio Call</h2>
            <button
              onClick={startCall}
              className="bg-sky-400 text-slate-900 px-4 py-2 rounded-lg font-semibold"
            >
              Start Call
            </button>
            <audio ref={audioRef} autoPlay playsInline controls={false} muted={false} />
            <p className="mt-3 text-sm opacity-80">{status}</p>
            <p className="mt-2 text-xs opacity-50 break-all">
              Share: {shareUrl}
            </p>
          </div>
        </div>
      );
}
