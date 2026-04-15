import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LoginForm } from '@/features/auth/login-form';

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string }>;
}) {
  const { next } = await searchParams;

  return (
    <div className="mx-auto max-w-md">
      <Card>
        <CardHeader>
          <CardTitle>Owner Sign In</CardTitle>
        </CardHeader>
        <CardContent>
          <LoginForm nextPath={next} />
        </CardContent>
      </Card>
    </div>
  );
}
