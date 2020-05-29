import sources from '../../data/sources.json';

export const federal_options = [
    { value: null, text: 'Any' },
    ...sources.federal
];

export const regional_options = [
    { value: null, text: 'Any' },
    ...sources.regional
];

export const local_options = [
    { value: null, text: 'Any' },
    ...sources.local
];

export const frequency_options = [
    { value: 0, text: 'Weekly' },
    { value: 1, text: 'Semi-Weekly' },
    { value: 2, text: 'Monthly' },
];