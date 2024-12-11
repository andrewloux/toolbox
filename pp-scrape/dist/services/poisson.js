"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.poissonService = exports.PoissonService = void 0;
class PoissonService {
    factorial(n) {
        if (n === 0 || n === 1)
            return 1;
        return n * this.factorial(n - 1);
    }
    poissonProbability(lambda, k) {
        return (Math.pow(lambda, k) * Math.exp(-lambda)) / this.factorial(k);
    }
    generateInterval(meanInterval) {
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
exports.PoissonService = PoissonService;
exports.poissonService = new PoissonService();
