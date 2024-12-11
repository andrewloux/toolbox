export class PoissonService {
  private factorial(n: number): number {
    if (n === 0 || n === 1) return 1;
    return n * this.factorial(n - 1);
  }

  private poissonProbability(lambda: number, k: number): number {
    return (Math.pow(lambda, k) * Math.exp(-lambda)) / this.factorial(k);
  }

  public generateInterval(meanInterval: number): number {
    // Generate a random interval following Poisson distribution
    const lambda = 1 / meanInterval;
    let p = Math.random();
    let k = 0;
    let cumulativeP = this.poissonProbability(lambda, k);

    while (p > cumulativeP) {
      k++;
      cumulativeP += this.poissonProbability(lambda, k);
    }

    // Convert k to milliseconds and add some minimum delay
    return Math.max(k * 1000, 500);
  }
}

export const poissonService = new PoissonService();
