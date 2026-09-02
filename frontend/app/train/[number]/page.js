import TrainClient from './TrainClient';

export const metadata = {
  title: 'Train Schedule — SmartRail',
  description: 'View complete train schedule with all stops, timings, platforms, and day offsets.',
};

export default function TrainPage() {
  return <TrainClient />;
}
