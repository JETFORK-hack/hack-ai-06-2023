const readApiBaseFromEnv = (): string => {
  // Get API base URL from env
  // Priority is given to same host in the browser when environemnt is production
  if (
    import.meta.env.PROD &&
    !document.location.host.startsWith("localhost")
  ) {
    return `https://${document.location.host}`;
  } else if (import.meta.env.BASE_URL && import.meta.env.BASE_URL !== "/") {
    return import.meta.env.BASE_URL;
  }
  return "http://localhost:8000";
};

export const basePath: string = readApiBaseFromEnv();
