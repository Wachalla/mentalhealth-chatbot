// Malaysian Mental Health Support Resources
// Source: Find A Helpline Malaysia directory

export interface HelplineResource {
  id: string;
  name: string;
  description: string;
  phone?: string;
  whatsapp?: string;
  hours?: string;
  availability: string;
  type: 'crisis' | 'counseling' | 'peer' | 'youth' | 'specialized';
  website?: string;
  languages: string[];
  free: boolean;
}

export const malaysianHelplines: HelplineResource[] = [
  {
    id: 'miasa',
    name: 'MIASA Crisis Helpline',
    description: 'Free 24/7 support by trained peers and volunteers',
    phone: '1-800-18-0066',
    whatsapp: '+6018-727-4454',
    hours: '24/7',
    availability: 'Always available',
    type: 'crisis',
    languages: ['English', 'Bahasa Malaysia', 'Mandarin', 'Tamil'],
    free: true,
    website: 'https://miasa.org.my'
  },
  {
    id: 'talian-kasih',
    name: 'Talian Kasih',
    description: 'Government-run hotline covering counseling and social support',
    phone: '15999',
    hours: '24/7',
    availability: 'Always available',
    type: 'counseling',
    languages: ['English', 'Bahasa Malaysia'],
    free: true
  },
  {
    id: 'talian-heal',
    name: 'Talian HEAL',
    description: 'Tele-counseling offering crisis and psychosocial support',
    phone: '15555',
    hours: 'Daily 8:00 - 24:00',
    availability: '16 hours daily',
    type: 'counseling',
    languages: ['English', 'Bahasa Malaysia'],
    free: true
  },
  {
    id: 'lifeline',
    name: 'Life Line Association Malaysia',
    description: 'Long-standing emotional support line',
    phone: '03-4265-7995',
    hours: 'Daily 12:00 - 22:00',
    availability: '10 hours daily',
    type: 'peer',
    languages: ['English', 'Bahasa Malaysia', 'Mandarin'],
    free: true
  },
  {
    id: 'pt-foundation',
    name: 'PT Foundation Peer Listening',
    description: 'Safe peer support for various communities',
    phone: '03-4044-4611',
    whatsapp: '+6019-353-5277',
    hours: 'Mon-Fri 10:00 - 18:00',
    availability: 'Weekdays business hours',
    type: 'peer',
    languages: ['English', 'Bahasa Malaysia'],
    free: true
  },
  {
    id: 'buddy-bear',
    name: 'Buddy Bear Helpline',
    description: 'Youth and child emotional support',
    phone: '1800-18-2327',
    hours: 'Daily 10:00 - 22:00',
    availability: '12 hours daily',
    type: 'youth',
    languages: ['English', 'Bahasa Malaysia'],
    free: true
  },
  {
    id: 'befrienders',
    name: 'Befrienders Kuala Lumpur',
    description: 'Emotional support and crisis intervention',
    phone: '03-7627-2929',
    hours: 'Daily 12:00 - 22:00',
    availability: '10 hours daily',
    type: 'crisis',
    languages: ['English', 'Bahasa Malaysia', 'Mandarin', 'Tamil'],
    free: true,
    website: 'https://befrienders.org.my'
  },
  {
    id: 'mercare',
    name: 'MERCARE Malaysia',
    description: 'Mental health crisis response team',
    phone: '010-926-8095',
    whatsapp: '+6010-926-8095',
    hours: '24/7 crisis response',
    availability: '24/7 emergencies',
    type: 'crisis',
    languages: ['English', 'Bahasa Malaysia'],
    free: true
  }
];

export const emergencyServices = {
  ambulance: '999',
  police: '999',
  fire: '999',
  generalEmergency: '999'
};

export const getHelplineByType = (type: HelplineResource['type']) => {
  return malaysianHelplines.filter(h => h.type === type);
};

export const getAvailableHelplines = () => {
  const now = new Date();
  const currentHour = now.getHours();
  const currentDay = now.getDay(); // 0 = Sunday, 6 = Saturday
  
  return malaysianHelplines.filter(helpline => {
    if (helpline.availability === 'Always available') return true;
    if (helpline.availability === '24/7 emergencies') return true;
    
    // Check if currently within operating hours
    const [startHour] = helpline.hours?.match(/(\d+):\d+/) || ['0'];
    const [endHour] = helpline.hours?.match(/(\d+):\d+/) || ['23'];
    
    const start = parseInt(startHour);
    const end = parseInt(endHour);
    
    if (currentDay >= 1 && currentDay <= 5) { // Weekdays
      return currentHour >= start && currentHour <= end;
    }
    
    return false;
  });
};
