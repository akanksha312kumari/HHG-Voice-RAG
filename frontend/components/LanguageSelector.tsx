import React from "react";
import { LanguageCode } from "../lib/types";
import { Globe } from "lucide-react";

interface Language {
  code: LanguageCode;
  name: string;
  native: string;
}

const LANGUAGES: Language[] = [
  { code: "as", name: "Assamese", native: "অসমীয়া" },
  { code: "bn", name: "Bengali", native: "বাংলা" },
  { code: "gu", name: "Gujarati", native: "ગુજરાતી" },
  { code: "hi", name: "Hindi", native: "हिन्दी" },
  { code: "kn", name: "Kannada", native: "ಕನ್ನಡ" },
  { code: "ml", name: "Malayalam", native: "മലയാളം" },
  { code: "mr", name: "Marathi", native: "मराठी" },
  { code: "ne", name: "Nepali", native: "नेपाली" },
  { code: "or", name: "Odia", native: "ଓଡ଼ିଆ" },
  { code: "pa", name: "Punjabi", native: "ਪੰਜਾਬੀ" },
  { code: "sa", name: "Sanskrit", native: "संस्कृतम्" },
  { code: "ta", name: "Tamil", native: "தமிழ்" },
  { code: "te", name: "Telugu", native: "తెలుగు" },
  { code: "ur", name: "Urdu", native: "اردو" },
];

interface LanguageSelectorProps {
  selected: LanguageCode;
  onSelect: (lang: LanguageCode) => void;
  disabled?: boolean;
}

export default function LanguageSelector({ selected, onSelect, disabled }: LanguageSelectorProps) {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium text-slate-400 flex items-center gap-2">
        <Globe size={16} /> Select Language
      </label>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-7 gap-2">
        {LANGUAGES.map((lang) => {
          const isSelected = selected === lang.code;
          return (
            <button
              key={lang.code}
              onClick={() => onSelect(lang.code)}
              disabled={disabled}
              className={`p-3 rounded-lg border flex flex-col items-start transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-teal-500
                ${isSelected 
                  ? "bg-teal-500/20 border-teal-500/50 text-teal-300" 
                  : "bg-zinc-900 border-zinc-800 text-slate-300 hover:bg-zinc-800 hover:border-zinc-700"}
                ${disabled ? "opacity-50 cursor-not-allowed" : ""}
              `}
            >
              <span className="text-sm font-semibold">{lang.name}</span>
              <span className="text-xs opacity-75">{lang.native}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
