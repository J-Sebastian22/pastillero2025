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
        this.proximosHorarios = data;
        console.log('Horarios:', data);
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