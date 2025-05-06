import { Card, CardDescription, CardFooter, CardHeader, CardTitle } from "../ui/card";

// Component for stat cards
export function StatCard({ icon, title, value, color }) {
  return (
    <Card className={`${color}`}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{value}</CardDescription>
      </CardHeader>
      {/* <CardContent>
          <p className="text-3xl font-semibold mt-2">{value}</p>
        </CardContent> */}
      <CardFooter>
        <div className="flex items-center justify-center">
          {icon}
        </div>
      </CardFooter>
    </Card>
  );
}
