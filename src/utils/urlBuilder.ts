interface JobParams {
  job_title: string;
  location: string;
  contract: string;
  region: string;
}

export const buildURLQuery = (params: Record<string, string>): string => {
  return Object.entries(params)
    .filter(([_, value]) => value != null && value !== '')
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join("&");
};

export const buildIndeedURL = ({ job_title, location, contract, region }: JobParams): string => {
  const query = buildURLQuery({
    q: job_title,
    l: location,
    sc: `0kf:jt(${contract});`,
    rbl: location,
    r: region,
  });

  return `https://${region}.indeed.com/jobs?${query}`
};
