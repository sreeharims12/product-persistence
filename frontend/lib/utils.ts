export function formatCurrencySymbol(currency: string = 'INR'): string {
  const code = (currency || 'INR').toUpperCase();
  switch (code) {
    case 'INR': return '₹';
    case 'USD': return '$';
    case 'EUR': return '€';
    case 'GBP': return '£';
    case 'JPY': return '¥';
    default: return '₹';
  }
}

export function formatPrice(price: number | null | undefined, currency: string = 'INR'): string {
  if (price === null || price === undefined) return 'N/A';
  const symbol = formatCurrencySymbol(currency);
  return `${symbol}${price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}
