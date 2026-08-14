// Placeholder home page
import VoiceRecorder from '../components/VoiceRecorder';
import LanguageSelector from '../components/LanguageSelector';
import TranscriptDisplay from '../components/TranscriptDisplay';
import AnswerCard from '../components/AnswerCard';
import LatencyDashboard from '../components/LatencyDashboard';
import GuardrailBadge from '../components/GuardrailBadge';

export default function Home() {
  return (
    <main>
      <h1>Voice RAG System</h1>
      <LanguageSelector />
      <VoiceRecorder />
      <TranscriptDisplay />
      <AnswerCard />
      <GuardrailBadge />
      <LatencyDashboard />
    </main>
  );
}
