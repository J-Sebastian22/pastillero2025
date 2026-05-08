import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Dashboards } from '../../services/dashboard';
import { Auth } from '../../services/auth';




@Component({
  selector: 'app-dashboard',
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class Dashboard {
  proximosHorarios: any[] = [];
  usuario: any;

  sidebarAbierto = false;
  // Summary widgets (static defaults, can be wired to real data)
  numMedicamentosActivos: number = 2;
  alertasHoy: number = 4;
  estadoPastillero: string = 'Conectado';

  constructor(
    private dashboardService: Dashboards,
    private auth: Auth,
    private router: Router
  ) {}

  ngOnInit() {
    this.usuario = this.auth.obtenerUsuario();
    if (this.usuario) {
      this.cargarProximosHorarios();
    }
  }

  cargarProximosHorarios() {
    this.dashboardService.getProximosHorarios(this.usuario.id).subscribe({
      next: (data: any) => {
        // Ordenar por `proxima_toma` de la más próxima a la más lejana
        this.proximosHorarios = (data || []).slice().sort((a: any, b: any) => {
          const at = a && a.proxima_toma ? new Date(a.proxima_toma).getTime() : Number.POSITIVE_INFINITY;
          const bt = b && b.proxima_toma ? new Date(b.proxima_toma).getTime() : Number.POSITIVE_INFINITY;
          return at - bt;
        });
        console.log('Horarios ordenados:', this.proximosHorarios);
      },
      error: (err: any) => console.error('Error:', err)
    });
  }

  irA(ruta: string) {
    this.router.navigate([ruta]);
    this.sidebarAbierto = false;
  }

  toggleSidebar() {
    this.sidebarAbierto = !this.sidebarAbierto;
  }
}