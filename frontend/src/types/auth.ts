
export type Role = "student" | "professor" | "admin";

export const redirectByRole = (role: Role, router: any) => {
    router.push(`/dashboard/${role}`);
};

