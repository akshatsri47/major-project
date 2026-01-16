"use client"
import { parseAppSegmentConfig } from "next/dist/build/segment-config/app/app-segment-config"
import { useEffect,useRef,useState } from "react"
export default function CallPage({params:}:{params:{room:string}}){
    const roomId = params.room
    const [status,setstatus] = useState("idle")
    const pcRef = useRef<RTCPeerConnection | null>(null);
    const audioRef = useRef<HTMLAudioElement | null>(null);
    
    
    async function startCall(){
        setstatus("requestion microphone")
        const stream = await navigator.mediaDevices.getUserMedia({audio:true})
        const pc = new RTCPeerConnection({
            iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
          });
        
        pcRef.current = pc;
        
      
    }
}
