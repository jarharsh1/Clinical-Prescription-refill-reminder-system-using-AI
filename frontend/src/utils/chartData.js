function countBy(items, keyFn) {
  return items.reduce((acc, item) => {
    const key = keyFn(item);
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});
}

export function riskLevelChart(patients) {
  const counts = countBy(patients, (p) => p.risk.level);
  return {
    labels: ['Low', 'Medium', 'High'],
    datasets: [
      {
        data: [counts.Low || 0, counts.Medium || 0, counts.High || 0],
        backgroundColor: ['#10B981', '#F59E0B', '#EF4444'],
      },
    ],
  };
}

export function statusChart(patients) {
  const counts = patients.reduce(
    (acc, p) => {
      if (p.risk.status === 'overdue') acc.overdue++;
      else if (p.risk.status === 'due_soon') acc.dueSoon++;
      else acc.onTrack++;
      return acc;
    },
    { onTrack: 0, dueSoon: 0, overdue: 0 },
  );
  return {
    labels: ['On Track', 'Due Soon', 'Overdue'],
    datasets: [
      {
        label: 'Patient Count',
        data: [counts.onTrack, counts.dueSoon, counts.overdue],
        backgroundColor: ['#22C55E', '#F59E0B', '#EF4444'],
      },
    ],
  };
}

export function pipelineChart(patients) {
  const counts = patients.reduce(
    (acc, p) => {
      if (p.ops_issue === 'None') acc.processed++;
      else if (p.ops_issue === 'Insurance Mismatch') acc.insurance++;
      else acc.other++;
      return acc;
    },
    { processed: 0, insurance: 0, other: 0 },
  );
  return {
    labels: ['Processed', 'Pending Insurance', 'Other Exceptions'],
    datasets: [
      {
        data: [counts.processed, counts.insurance, counts.other],
        backgroundColor: ['#22C55E', '#F59E0B', '#6B7280'],
      },
    ],
  };
}

export function exceptionChart(patients) {
  const counts = countBy(
    patients.filter((p) => p.ops_issue !== 'None'),
    (p) => p.ops_issue,
  );
  return {
    labels: Object.keys(counts),
    datasets: [
      {
        label: 'Exception Count',
        data: Object.values(counts),
        backgroundColor: ['#EF4444', '#F59E0B', '#EAB308'],
      },
    ],
  };
}

export function clinicianChart(patients) {
  const counts = countBy(patients, (p) => p.doctor);
  return {
    labels: Object.keys(counts),
    datasets: [{ label: 'Patients', data: Object.values(counts), backgroundColor: '#4F46E5' }],
  };
}

export function medicationChart(patients) {
  const counts = countBy(patients, (p) => p.medication);
  const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 5);
  return {
    labels: sorted.map((m) => m[0]),
    datasets: [{ label: 'Prescriptions', data: sorted.map((m) => m[1]), backgroundColor: '#10B981' }],
  };
}

export function conditionChart(patients) {
  const counts = countBy(patients, (p) => p.condition);
  return {
    labels: Object.keys(counts),
    datasets: [
      { data: Object.values(counts), backgroundColor: ['#3B82F6', '#F97316', '#8B5CF6', '#FACC15'] },
    ],
  };
}
