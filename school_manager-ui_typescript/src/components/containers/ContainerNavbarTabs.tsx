export interface ITab {
    name: string,
    location: string,
    underTab?: boolean
}

export const Tabs: ITab[] = [
    {
        name: 'דו"ח פיננסי',
        location: '/finance-report'
    },
    {
        name: 'סל תשלומים',
        location: '/finance-report/payments-basket',
        underTab: true
    },
    {
        name: 'מצבת תקבולים',
        location: '/periodic-reception'
    },
    {
        name: 'סל תקבולים',
        location: '/periodic-reception/reception-basket',
        underTab: true
    },
    {
        name: 'דו"ח תנועות',
        location: '/transactions-report'
    },
    {
        name: 'ייבוא נתונים מקובץ',
        location: '/import-data'
    },
    {
        name: 'חשבונות בנק - עובר ושב',
        location: '/bank-account'
    }
]