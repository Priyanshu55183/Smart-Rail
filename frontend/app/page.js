import HomeClient from './HomeClient';

export const metadata = {
  title: 'SmartRail — AI-Powered Railway Journey Planner',
  description: 'Find the best train routes across India using graph algorithms, ML delay prediction, and intelligent scoring. SmartRail — the smart way to travel by rail.',
};

export default function HomePage() {
  return <HomeClient />;
}
