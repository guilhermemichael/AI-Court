import { z } from 'zod';

export const casePayloadSchema = z.object({
  title: z.string().min(3).max(180),
  plaintiff_name: z.string().min(1).max(80),
  defendant_name: z.string().min(1).max(80),
  plaintiff_argument: z.string().min(10).max(8000),
  defendant_argument: z.string().min(10).max(8000),
  conflict_type: z.string().min(2).max(80),
  drama_level: z.number().int().min(1).max(10),
  allow_precedents: z.boolean(),
});

export const defaultCaseForm = casePayloadSchema.parse({
  title: 'O Ultimo Pedaco de Lasanha',
  plaintiff_name: 'Parte Ofendida',
  defendant_name: 'Reu da Geladeira',
  plaintiff_argument: 'Eu guardei a lasanha para o almoco do dia seguinte e ela desapareceu sem qualquer aviso previo.',
  defendant_argument: 'Havia fome extraordinaria, ausencia de etiqueta visivel e boa-fe culinaria do meu lado.',
  conflict_type: 'conflito alimentar',
  drama_level: 8,
  allow_precedents: true,
});
