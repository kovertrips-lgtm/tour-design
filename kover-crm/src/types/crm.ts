export interface Tag {
    id: string;
    name: string;
    color: string; // Hex
}

export interface Task {
    id: string;
    text: string;
    due_date: number; // timestamp
    is_completed: boolean;
    type: 'call' | 'meeting' | 'todo';
}

export interface Message {
    id: string;
    type: 'sms' | 'email' | 'tg' | 'ig' | 'system' | 'note';
    author: string;
    text: string;
    created_at: number; // timestamp
    direction?: 'in' | 'out';
    attachments?: string[];
}

export interface DealField {
    label: string;
    value: string | number;
    type: 'text' | 'select' | 'date' | 'money';
    key: string;
}

export interface Deal {
    id: string;
    title: string;
    price: number;
    currency: string;
    status_column_id: string; // Refers to the column
    contact_name: string;
    contact_company?: string;
    contact_phone?: string;
    contact_email?: string;
    responsible: string; // e.g., 'Ivan Ivanov'
    source: string; // e.g., 'Instagram'
    created_at: number;
    tags: Tag[];
    fields: DealField[]; // Custom fields
    history: Message[]; // The Activity Feed
}

// Columns Configuration
export const PIPELINE_COLUMNS = [
    { id: 'new', title: 'New Request', color: '#99ccff' },
    { id: 'work', title: 'In Progress', color: '#ffff99' },
    { id: 'answered', title: 'Answered', color: '#ffcc99' },
    { id: 'details', title: 'Data Received', color: '#ccffcc' },
    { id: 'invoice', title: 'Invoice Sent', color: '#ccffff' },
    { id: 'paid', title: 'Payment Received', color: '#ccff99' },
];

// Mock Data
export const MOCK_DEALS: Deal[] = [
    {
        id: '1420392',
        title: 'Tour to Alps #3284',
        price: 45000,
        currency: 'CZK',
        status_column_id: 'new',
        contact_name: 'Katusha333',
        contact_company: 'Instagram',
        contact_phone: '+420 777 123 456',
        responsible: 'Manager Alex',
        source: 'Instagram',
        created_at: Date.now() - 86400000,
        tags: [{ id: '1', name: 'VIP', color: '#ff5e5e' }],
        fields: [
            { key: 'budget', label: 'Budget', value: 50000, type: 'money' },
            { key: 'people', label: 'Guests', value: '2 Adults', type: 'text' }
        ],
        history: [
            { id: '1', type: 'system', author: 'System', text: 'Deal created', created_at: Date.now() - 86400000 },
            { id: '2', type: 'ig', author: 'katusha333', direction: 'in', text: 'Hello! How much is the tour?', created_at: Date.now() - 86000000 },
            { id: '3', type: 'ig', author: 'Manager Alex', direction: 'out', text: 'Hi! It starts from 450 EUR per person.', created_at: Date.now() - 85000000 },
        ]
    },
    {
        id: '1420395',
        title: 'Skiing / Soelden',
        price: 1200,
        currency: 'EUR',
        status_column_id: 'work',
        contact_name: 'John Doe',
        contact_company: 'Google Search',
        contact_phone: '+1 555 0199',
        responsible: 'Manager Maria',
        source: 'Website',
        created_at: Date.now() - 172800000,
        tags: [{ id: '2', name: 'Sledding', color: '#4c8bf5' }, { id: '3', name: 'Hot', color: '#ff5e5e' }],
        fields: [],
        history: []
    },
    {
        id: '1420396',
        title: 'Zell am See Group',
        price: 240000,
        currency: 'CZK',
        status_column_id: 'paid',
        contact_name: 'Big Corp Ltd',
        contact_company: 'Partner',
        responsible: 'Manager Ivan',
        source: 'Referral',
        created_at: Date.now() - 432000000,
        tags: [{ id: '4', name: 'B2B', color: '#6ccb5f' }],
        fields: [],
        history: []
    }
];
