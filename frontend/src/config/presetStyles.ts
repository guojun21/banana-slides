// Preset PPT style configuration with i18n support

export interface PresetStyle {
  id: string;
  nameKey: string;  // i18n key for name
  descriptionKey: string;  // i18n key for description
  previewImage?: string;
}

// Style IDs map to i18n keys in presetStyles namespace
export const PRESET_STYLES: PresetStyle[] = [
  {
    id: 'business-simple',
    nameKey: 'presetStyles.businessSimple.name',
    descriptionKey: 'presetStyles.businessSimple.description',
    previewImage: '/preset-previews/business-simple.webp',
  },
  {
    id: 'tech-modern',
    nameKey: 'presetStyles.techModern.name',
    descriptionKey: 'presetStyles.techModern.description',
    previewImage: '/preset-previews/tech-modern.webp',
  },
  {
    id: 'academic-formal',
    nameKey: 'presetStyles.academicFormal.name',
    descriptionKey: 'presetStyles.academicFormal.description',
    previewImage: '/preset-previews/academic-formal.webp',
  },
];

// Helper function to get style with translated values
export const getPresetStyleWithTranslation = (
  style: PresetStyle,
  t: (key: string) => string
): { id: string; name: string; description: string; previewImage?: string } => {
  return {
    id: style.id,
    name: t(style.nameKey),
    description: t(style.descriptionKey),
    previewImage: style.previewImage,
  };
};
